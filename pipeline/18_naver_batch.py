import os
import sys
import io
import time
import re
from playwright.sync_api import sync_playwright
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def parse_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        man = int(re.sub(r'[^0-9]', '', parts[1])) * 10000 if re.sub(r'[^0-9]', '', parts[1]) else 0
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
    except: return []

def get_naver_lowest_ask(page, complex_no, ptpNo):
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&ptpNo={ptpNo}&prcSort=asc"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        try:
            page.locator("label:has-text('동일매물 묶기')").click(timeout=2000)
            time.sleep(1)
        except: pass

        cards = page.locator(".item_inner").all()[:10]
        for card in cards:
            text = card.inner_text()
            if "지분" in text or "경매" in text: continue
            
            try:
                p_text = card.locator(".price").first.inner_text().strip()
                p_num = parse_price(p_text)
                if p_num >= 500000000: # 최소 5억 시세 방어막
                    return p_num
            except: pass
        return None
    except: return None

def run_naver_50_master():
    print("=======================================================================")
    print("💎 [18번 배치] 전체 50개 단지 네이버 호가 스캔 & DB ATH 결합 (MDD) 💎")
    print("=======================================================================")
    
    complexes = supabase.table("complexes").select("*").execute().data
    if not complexes: return
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        for idx, c in enumerate(complexes):
            cid = c["id"]
            c_no = c["complex_no"]
            name = c["name"]
            
            print(f"\n▶ [{idx+1}/50] 🏢 {name} 크롤링 및 MDD 결산 중...")
            pyeongs = fetch_pyeong_meta_dyn(page, c_no)
            
            # DB(rtms_transactions)에서 해당 단지의 최고가(ATH) 목록 불러오기
            try:
                # Supabase REST로 해당 단지 거래기록의 역대 최고가를 면적(match_key)별로 산출
                res = supabase.table("rtms_transactions").select("match_key_area, deal_price, deal_date").eq("complex_id", cid).execute().data
                ath_map = {}
                for deal in res:
                    mk = deal["match_key_area"]
                    pr = deal["deal_price"]
                    if mk not in ath_map or pr > ath_map[mk]["price"]:
                        ath_map[mk] = {"price": pr, "date": deal["deal_date"]}
            except Exception as e:
                ath_map = {}
                
            for p_meta in pyeongs:
                ptpNo = p_meta["ptpNo"]
                mk = p_meta["match_key"]
                p_name = p_meta["pyeongNm"]
                
                # 최고가가 없으면(10년치 거래 없으면) 패스
                if mk not in ath_map: continue
                
                ath_price = ath_map[mk]["price"]
                ath_date = ath_map[mk]["date"]
                
                # 네이버 실시간 호가 조회
                current_ask = get_naver_lowest_ask(page, c_no, ptpNo)
                if not current_ask: continue
                
                mdd = round(((current_ask - ath_price) / ath_price) * 100, 2)
                
                stat_data = {
                    "complex_id": cid,
                    "pyeong_name": p_name,
                    "naver_ptp_no": ptpNo,
                    "match_key_area": mk,
                    "current_lowest_ask": current_ask,
                    "highest_deal_price": ath_price,
                    "highest_deal_date": ath_date,
                    "mdd_rate": mdd
                }
                supabase.table("pyeong_stats").upsert(stat_data, on_conflict="complex_id, match_key_area").execute()
                
                c_str = f"{current_ask // 100000000}억 {((current_ask % 100000000) // 10000)}만".replace(" 0만", "")
                h_str = f"{ath_price // 100000000}억 {((ath_price % 100000000) // 10000)}만".replace(" 0만", "")
                print(f"   ✅ [전용 {mk}㎡] 호가 {c_str} vs 최고가 {h_str} ({ath_date}) 👉 MDD: {mdd}%")
            
            # 네이버 어뷰징 타임아웃 밴 회피 로직
            time.sleep(1.5)
            
        browser.close()
    print("\n🎉 전국 50대장 모든 평형의 실시간 최저호가 및 하락률(MDD) 결산 완료!")

if __name__ == "__main__":
    run_naver_50_master()
