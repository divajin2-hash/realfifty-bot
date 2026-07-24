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

# The official Move-in Rights (분양/입주권) Endpoint
url = "http://apis.data.go.kr/1613000/RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade"

def format_price(p_str):
    try:
        return int(p_str.replace(",", "").strip()) * 10000
    except:
        return 0

def fetch_month_rights(lawd_cd, ymd):
    params = {
        "serviceKey": RTMS_KEY,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": ymd,
        "numOfRows": "2000",
        "pageNo": "1"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        # 403 or others
        if res.status_code != 200:
            return []
        
        root = ET.fromstring(res.content)
        resultMsg = root.findtext(".//resultMsg", "")
        if "NORMAL SERVICE" not in resultMsg.upper() and resultMsg != "OK":
            return []
            
        trades = []
        for item in root.findall(".//item"):
            apt = item.findtext("aptNm", "")
            if not apt: continue
            
            p = format_price(item.findtext("dealAmount"))
            mk = int(round(float(item.findtext("excluUseAr"))))
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

def run_rights_collector():
    print("Fetching complexes from Supabase...")
    res = supabase.table("complexes").select("*").execute()
    complexes = res.data

    # Map LAWD_CD to complexes we care about
    # e.g., 11680 (Gangnam) -> [DH Firstier, ...], 11740 (Gangdong) -> [Olympic Park Foreon]
    lawd_map = {}
    for c in complexes:
        lawd = c["bjd_code"][:5]
        if lawd not in lawd_map:
            lawd_map[lawd] = []
        lawd_map[lawd].append(c)
        
    year_months = [f"{y}{m:02d}" for y in range(2023, 2027) for m in range(1, 13) if not (y == 2026 and m > 7) and not (y == 2023 and m < 1)]

    print(f"Targeting {len(lawd_map)} LAWD_CDs for Move-in Rights over 2023-2026.07")
    
    total_inserted = 0
    
    for lawd, comps in lawd_map.items():
        print(f"\n[LAWD: {lawd}] Retrieving {len(year_months)} months of rights trades...")
        all_trades = []
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_ymd = {executor.submit(fetch_month_rights, lawd, ymd): ymd for ymd in year_months}
            for future in as_completed(future_to_ymd):
                ymd = future_to_ymd[future]
                res = future.result()
                if res:
                    all_trades.extend(res)
                    
        # Filter for our complex names
        valid_inserts = []
        for t in all_trades:
            # Match to our complexes
            raw_apt = t["aptNm"]
            
            matched_c_id = None
            for c in comps:
                # Name matching (Simple)
                db_name = c["name"].replace(" ", "")
                if db_name in raw_apt or raw_apt in db_name:
                    matched_c_id = c["id"]
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
            print(f"Found {len(valid_inserts)} relevant move-in rights. Inserting to DB...")
            chunk_size = 500
            for i in range(0, len(valid_inserts), chunk_size):
                chunk = valid_inserts[i:i+chunk_size]
                supabase.table("rtms_transactions").upsert(
                    chunk, on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", ignore_duplicates=True
                ).execute()
            total_inserted += len(valid_inserts)
        else:
            print(f"LAWD {lawd}: No relevant trades matched our complexes.")
            
    print(f"\\nFINISH. Inserted a total of {total_inserted} move-in right trades.")

if __name__ == "__main__":
    run_rights_collector()
