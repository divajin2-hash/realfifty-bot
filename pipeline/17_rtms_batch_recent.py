import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY")

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run():
    complexes = supabase.table("complexes").select("*").execute().data
    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    # Generate YYYYMM strings from 202408 to 202608
    ymds = []
    for y in range(2024, 2027):
        for m in range(1, 13):
            if y == 2024 and m < 8: continue
            if y == 2026 and m > 8: continue
            ymds.append(f"{y}{m:02d}")
            
    for ymd in ymds:
        print(f"Fetching {ymd}...")
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
                if res.status_code == 200:
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
                        area_exact = float(item.findtext("excluUseAr"))
                        mk = int(round(area_exact))
                        if matched_c["id"] == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(area_exact - 82.23) < 0.01:
                            mk = 83
                            
                        d_str = f"{ymd[:4]}-{int(ymd[4:]):02d}-{int(item.findtext('dealDay')):02d}"
                        deal_type = item.findtext("dealingGbn", " ")
                        
                        trades_to_insert.append({
                            "complex_id": matched_c["id"],
                            "match_key_area": mk,
                            "deal_date": d_str,
                            "deal_price": price,
                            "floor": int(item.findtext("floor", "0")),
                            "exclusive_area_exact": area_exact,
                            "transaction_type": deal_type
                        })
            except: pass
            time.sleep(0.05)
            
        if trades_to_insert:
            supabase.table("rtms_transactions").upsert(
                trades_to_insert, 
                on_conflict="complex_id, match_key_area, deal_date, deal_price, floor"
            ).execute()

if __name__ == "__main__":
    run()
