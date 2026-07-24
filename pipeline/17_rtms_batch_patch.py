import os
import sys
import io
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY")

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run_rtms_update_batch():
    print("=========================================================")
    print("🔥 [긴급 패치] 누락된 24년 8월 ~ 26년 7월 최신 데이터 긴급 수혈 🔥")
    print("=========================================================")
    
    complexes = supabase.table("complexes").select("*").execute().data
    if not complexes: return
        
    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    # 동적 현재 날짜 파악
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    
    # 누락되었던 2024년 8월부터 현재까지 순회
    # (이미 2024.08 이전은 구축 완료됨)
    years = range(2024, current_year + 1)
    months = range(1, 13)
    
    total_inserted = 0
    
    for y in years:
        for m in months:
            # 2024년 7월 이전은 패스
            if y == 2024 and m <= 7: continue
            # 현재 연월 이후 미래는 패스
            if y == current_year and m > current_month: continue
            
            ymd = f"{y}{m:02d}"
            print(f"\n▶ 📅 추가 스캔 연월: {ymd}")
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
                        day = item.findtext("dealDay")
                        d_str = f"{y}-{m:02d}-{int(day):02d}"
                        floor = int(item.findtext("floor", "0"))
                        
                        trades_to_insert.append({
                            "complex_id": matched_c["id"],
                            "match_key_area": mk,
                            "deal_date": d_str,
                            "deal_price": price,
                            "floor": floor
                        })
                except Exception:
                    pass
                
                time.sleep(0.05)
                
            if trades_to_insert:
                try:
                    supabase.table("rtms_transactions").upsert(
                        trades_to_insert, 
                        on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", 
                        ignore_duplicates=True
                    ).execute()
                    total_inserted += len(trades_to_insert)
                    print(f"   ✅ {ymd} -> {len(trades_to_insert)}건 추가 완료 (누적: {total_inserted}건)")
                except Exception:
                    pass

    print(f"\n🎉 누락되었던 최근 2년 치 최신 실거래가 총 {total_inserted}건 수혈 완벽 종료!")

if __name__ == "__main__":
    run_rtms_update_batch()
