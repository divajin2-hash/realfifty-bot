import os
import sys
import io
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
RTMS_KEY = os.environ.get("RTMS_API_KEY")

if not URL or not KEY or not RTMS_KEY:
    print("❗ 에러: .env 파일에 필요한 키가 없습니다.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run_daily_rtms_crawler():
    print("🚀 [31번] 국토교통부 실거래가 최근 2개월 수집 (데일리 갱신) 시작...")
    
    complexes = supabase.table("complexes").select("*").execute().data
    if not complexes:
        print("DB에 저장된 아파트 단지가 없습니다.")
        return

    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    # 이번 달과 지난 달을 대상으로 조회 (실거래가 신고는 30일 이내)
    now = datetime.now()
    last_month_dt = (now.replace(day=1) - timedelta(days=1))
    
    target_ymds = [
        last_month_dt.strftime("%Y%m"),
        now.strftime("%Y%m")
    ]
    
    total_inserted = 0
    
    for ymd in target_ymds:
        print(f"\n▶ 📅 조회 연월: {ymd}")
        trades_to_insert = []
        
        for lawd_cd, apts in lawd_map.items():
            params = {
                "serviceKey": safe_key,
                "LAWD_CD": lawd_cd,
                "DEAL_YMD": ymd,
                "numOfRows": "2000",
                "pageNo": "1"
            }
            
            try:
                res = requests.get(url, params=params, timeout=10)
                if res.status_code != 200: continue
                root = ET.fromstring(res.content)
                
                for item in root.findall(".//item"):
                    item_apt = item.findtext("aptNm")
                    if not item_apt: continue
                    
                    matched_c = None
                    for c in apts:
                        db_name = c["name"].replace("(", "").replace(")", "").replace(" ", "")
                        api_name = item_apt.replace("(", "").replace(")", "").replace(" ", "")
                        if db_name in api_name or api_name in db_name:
                            matched_c = c
                            break
                            
                    if not matched_c: continue
                    
                    price = format_price(item.findtext("dealAmount"))
                    mk = int(float(item.findtext("excluUseAr")))
                    day = int(item.findtext("dealDay", "1"))
                    y = int(item.findtext("dealYear", ymd[:4]))
                    m = int(item.findtext("dealMonth", ymd[4:]))
                    d_str = f"{y}-{m:02d}-{day:02d}"
                    floor = int(item.findtext("floor", "0"))
                    
                    trades_to_insert.append({
                        "complex_id": matched_c["id"],
                        "match_key_area": mk,
                        "deal_date": d_str,
                        "deal_price": price,
                        "floor": floor
                    })
            except Exception as e:
                pass
            
            time.sleep(0.05) # Rate Limit 방지
            
        if trades_to_insert:
            try:
                supabase.table("rtms_transactions").upsert(
                    trades_to_insert, 
                    on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", 
                    ignore_duplicates=True
                ).execute()
                total_inserted += len(trades_to_insert)
                print(f"   ✅ {ymd} -> {len(trades_to_insert)}건 실거래 수집/갱신 완료")
            except Exception as e:
                print(f"      [!] DB 적재 지연: {e}")
                pass
        else:
            print(f"   🤔 {ymd} 월에는 아직 등록된 대상 단지 실거래가 없습니다.")

    print(f"\n🎉 방금까지 체결 등록된 최근 실거래 총 {total_inserted}건 반영 완료!")

if __name__ == "__main__":
    run_daily_rtms_crawler()
