import os
import sys
import io
import time
import re
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from datetime import datetime, date
from playwright.sync_api import sync_playwright
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY")

def parse_korean_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        digits_only = re.sub(r'[^0-9]', '', parts[1])
        man = int(digits_only) * 10000 if digits_only else 0
        return eok + man
    return 0

def fetch_pyeong_meta_dyn(page, complex_no):
    api_url = f"https://new.land.naver.com/api/complexes/{complex_no}"
    try:
        r = page.goto(api_url)
        data = r.json()
        pyeongs = []
        for p in data.get("complexPyeongDetailList", []):
            ptpNo = p.get("ptpNo")
            pyeongNm = p.get("pyeongNm")
            exclusive = p.get("exclusiveArea")
            if not ptpNo or not exclusive: continue
            
            match_key = int(float(exclusive))
            if not any(x["match_key"] == match_key for x in pyeongs):
                pyeongs.append({
                    "ptpNo": str(ptpNo),
                    "pyeongNm": pyeongNm,
                    "match_key": match_key
                })
        return pyeongs
    except Exception:
        return []

def get_naver_ask_exact(page, complex_no, ptpNo):
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&ptpNo={ptpNo}&prcSort=asc"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        try:
            page.locator("label:has-text('동일매물 묶기')").click(timeout=1000)
            time.sleep(0.5)
        except: pass

        cards = page.locator(".item_inner").all()[:10]
        for card in cards:
            text = card.inner_text().replace('\n', ' ')
            if "지분" in text or "경매" in text: continue
            
            try:
                price_text = card.locator(".price").first.inner_text().strip()
                price_num = parse_korean_price(price_text)
                if price_num >= 2000000000: # 20억 방어 필터
                    return price_num
            except: pass
        return None
    except:
        return None

def fetch_and_save_rtms(lawd_cd, apt_name, complex_id):
    years = [2021, 2022, 2023, 2024]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    
    ath_dict = {}
    trades_to_insert = []
    
    print(f"   [국토부 API 연동] {apt_name} 2021~2024년 핫사이클 정밀 탐색 중...")
    
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    for y in years:
        for m in months:
            ymd = f"{y}{m}"
            if y == 2024 and int(m) > 7: continue 
            
            params = {
                "serviceKey": safe_key,
                "LAWD_CD": lawd_cd,
                "DEAL_YMD": ymd,
                "numOfRows": "1000",
                "pageNo": "1"
            }
            
            try:
                res = requests.get(url, params=params, timeout=10)
                if res.status_code != 200: continue
                root = ET.fromstring(res.content)
                
                for item in root.findall(".//item"):
                    # 공공데이터포털 업그레이드 API 태그명으로 변경 완
                    item_apt = item.findtext("aptNm")
                    if not item_apt or apt_name not in item_apt: continue 
                    
                    price_str = item.findtext("dealAmount").replace(",", "").strip()
                    price = int(price_str) * 10000
                    area_str = item.findtext("excluUseAr")
                    match_key = int(float(area_str)) 
                    
                    day = item.findtext("dealDay")
                    date_str = f"{y}-{m}-{int(day):02d}"
                    floor_txt = item.findtext("floor", "0")
                    floor = int(floor_txt) if floor_txt else 0
                    
                    if match_key not in ath_dict or price > ath_dict[match_key]["price"]:
                        ath_dict[match_key] = {"price": price, "date": date_str}
                        
                    trades_to_insert.append({
                        "complex_id": complex_id,
                        "match_key_area": match_key,
                        "deal_date": date_str,
                        "deal_price": price,
                        "floor": floor
                    })
            except Exception as e:
                pass
            
    if trades_to_insert:
        chunk_size = 500
        for i in range(0, len(trades_to_insert), chunk_size):
            try:
                supabase.table("rtms_transactions").upsert(
                    trades_to_insert[i:i+chunk_size], 
                    on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", 
                    ignore_duplicates=True
                ).execute()
            except: pass
    
    return ath_dict

def run_pipeline():
    print("==================================================================")
    print("🔥 [최종 점검] 국토부 V2 API 대응 + 네이버 찐호가 퓨전 마스터 돌입 🔥")
    print("==================================================================")
    
    complex_data = supabase.table("complexes").select("*").eq("name", "은마").execute().data
    if not complex_data: return
    c = complex_data[0]
    cid = c["id"]
    lawd_cd = c["bjd_code"][:5] 
    
    ath_dict = fetch_and_save_rtms(lawd_cd, c["name"], cid)
    
    if not ath_dict:
        print("   ❌ 국토부 데이터 추출 실패 (또는 은마 거래 없음)")
        return
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        print(f"\n▶ [{c['name']}] 찐평형 추출 및 MDD 크로스 퓨전 중...")
        pyeongs = fetch_pyeong_meta_dyn(page, c["complex_no"])
        
        found = False
        for p_meta in pyeongs:
            ptpNo = p_meta["ptpNo"]
            mk = p_meta["match_key"]
            p_name = p_meta["pyeongNm"]
            
            if mk not in ath_dict: continue
                
            ath_price = ath_dict[mk]["price"]
            ath_date = ath_dict[mk]["date"]
            
            current_ask = get_naver_ask_exact(page, c["complex_no"], ptpNo)
            
            if not current_ask:
                continue
                
            mdd = round(((current_ask - ath_price) / ath_price) * 100, 2)
            found = True
            
            stat_data = {
                "complex_id": cid,
                "pyeong_name": p_name,
                "naver_ptp_no": str(ptpNo),
                "match_key_area": mk,
                "current_lowest_ask": current_ask,
                "highest_deal_price": ath_price,
                "highest_deal_date": ath_date,
                "mdd_rate": mdd
            }
            supabase.table("pyeong_stats").upsert(stat_data, on_conflict="complex_id, match_key_area").execute()
            
            c_e = current_ask // 100000000; c_m = (current_ask % 100000000) // 10000
            h_e = ath_price // 100000000; h_m = (ath_price % 100000000) // 10000
            c_str = f"{c_e}억 {c_m}만" if c_m else f"{c_e}억"
            h_str = f"{h_e}억 {h_m}만" if h_m else f"{h_e}억"
            
            badge = "🔥급매구간" if mdd <= -20 else ("⭐기회구간" if mdd <= -10 else "😐보합세")
            
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"   ✅ {c['name']} [{p_name} | 전용 {mk}㎡]")
            print(f"      - 과거 최고가(ATH) : {h_str} ({ath_date} 거래됨)")
            print(f"      - 현재 최저호가    : {c_str} (방금 네이버 스크래핑)")
            print(f"      - 최종 MDD 하락률  : {badge} [ {mdd}% ]")
            print(f"   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            
        if not found:
            print("   ❌ 매칭된 호가/실거래 데이터가 없어 MDD 산출 실패")
            
        browser.close()

if __name__ == "__main__":
    run_pipeline()
