import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY")

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run_missing_patch():
    print("🚀 누락된 4개 단지 10년치 국토부 실거래가 핀포인트 수집 시작...")
    
    complexes = supabase.table("complexes").select("*").execute().data
    
    missing_map = {
        "잠실주공(5단지)": ["주공아파트 5단지"],
        "현대(6 7차)": ["현대6차", "현대7차"],
        "선경(1 2차)": ["선경1차", "선경2차"],
        "신반포(한신4차)": ["신반포4"]
    }
    
    target_apts = [c for c in complexes if c["name"] in missing_map]
    
    lawd_map = {}
    for c in target_apts:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    now = datetime.now()
    years = range(2014, 2027)
    months = range(1, 13)
    
    total_inserted = 0
    
    for y in years:
        for m in months:
            if y == 2026 and m > 7: continue
            
            ymd = f"{y}{m:02d}"
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
                            allowed_names = missing_map.get(c["name"], [])
                            for allowed in allowed_names:
                                if allowed in item_apt:
                                    matched_c = c
                                    break
                            if matched_c: break
                                
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
                    print(f"[{ymd}] 수집 완료: {len(trades_to_insert)}건 (누적 {total_inserted}건)")
                except Exception as e:
                    print(f"DB 저장 에러: {e}")

    print(f"\n✅ 누락 단지 4곳 {total_inserted}건 실거래가 수집 완벽 패치 완료!")

if __name__ == "__main__":
    run_missing_patch()
