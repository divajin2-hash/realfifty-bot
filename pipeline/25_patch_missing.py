import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('pipeline/.env')

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = unquote(os.environ.get("RTMS_API_KEY"))

URL_APT = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

# The real mapping for the missing ones
missing_fixes = {
    "선경(1 2차)": ["선경1차", "선경2차", "선경"],
    "신반포(한신4차)": ["신반포4차", "한신4차", "한신4"],
    "장미(1차)": ["장미1차", "장미1", "장미2", "장미3", "장미아파트"],
    "현대(1~7차)": ["현대1차", "현대2차", "현대3차", "현대4차", "현대5차", "현대6차", "현대7차", "현대 1차", "압구정현대"],
    "현대(6 7차)": ["현대6차", "현대7차"],
    "현대(신현대)": ["신현대"],
    "잠실주공(5단지)": ["주공5단지", "잠실주공5", "주공아파트 5"],
}

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def fetch_pure_trades(url, lawd_cd, ymd):
    params = {
        "serviceKey": RTMS_KEY,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": ymd,
        "numOfRows": "3000",
        "pageNo": "1"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200: return []
        root = ET.fromstring(res.content)
        
        trades = []
        for item in root.findall(".//item"):
            dealing = item.findtext("dealingGbn", "")
            if "직거래" in dealing: continue
                
            apt = item.findtext("aptNm", "")
            if not apt: continue
            
            p = format_price(item.findtext("dealAmount"))
            exclu = float(item.findtext("excluUseAr"))
            mk = int(round(exclu))
            y = item.findtext("dealYear")
            m = int(item.findtext("dealMonth"))
            d = int(item.findtext("dealDay"))
            floor = int(item.findtext("floor", "0"))
            deal_date = f"{y}-{m:02d}-{d:02d}"
            
            trades.append({
                "aptNm": apt.replace(" ", ""),
                "match_key_area": mk,
                "deal_date": deal_date,
                "deal_price": p,
                "floor": floor
            })
        return trades
    except Exception as e:
        return []

def run_patch():
    complexes = supabase.table("complexes").select("*").execute().data
    target_comps = []
    
    for c in complexes:
        if c["name"] in missing_fixes:
            target_comps.append(c)
            
    lawd_map = {}
    for c in target_comps:
        lawd = c["bjd_code"][:5]
        if lawd not in lawd_map: lawd_map[lawd] = []
        lawd_map[lawd].append(c)
        
    year_months = [f"{y}{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if not (y == 2026 and m > 7)]

    print("Fetching missing data for specific complexes...")
    
    total = 0
    for lawd, comps in lawd_map.items():
        print(f"Processing LAWD {lawd} for {len(comps)} complexes...")
        all_apt = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            fut_apt = {executor.submit(fetch_pure_trades, URL_APT, lawd, ymd): ymd for ymd in year_months}
            for fut in as_completed(fut_apt):
                r = fut.result()
                if r: all_apt.extend(r)
                
        valid_inserts = []
        for t in all_apt:
            raw_apt = t["aptNm"]
            matched_c_id = None
            for c in comps:
                c_name = c["name"]
                allowed_names = missing_fixes.get(c_name, [])
                
                # Check mapping
                for allowed in allowed_names:
                    if allowed in raw_apt or raw_apt in allowed:
                        matched_c_id = c["id"]
                        break
                if matched_c_id:
                    break
            
            if matched_c_id:
                valid_inserts.append({
                    "complex_id": matched_c_id,
                    "match_key_area": t["match_key_area"],
                    "deal_date": t["deal_date"],
                    "deal_price": t["deal_price"],
                    "floor": t["floor"]
                })
                
        if valid_inserts:
            chunk_size = 500
            for i in range(0, len(valid_inserts), chunk_size):
                chunk = valid_inserts[i:i+chunk_size]
                supabase.table("rtms_transactions").upsert(
                    chunk, on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", ignore_duplicates=True
                ).execute()
            total += len(valid_inserts)
            print(f" -> Inserted {len(valid_inserts)} clean trades.")

    print(f"Done. Rebuilt {total} pure trades.")

if __name__ == "__main__":
    run_patch()
