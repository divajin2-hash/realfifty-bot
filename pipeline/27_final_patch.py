import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('pipeline/.env')

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = unquote(os.environ.get("RTMS_API_KEY"))

missing_fixes = {
    "선경(1 2차)": ["선경1차", "선경2차", "선경"],
    "신반포(한신4차)": ["신반포4차", "신반포4", "한신4차", "한신4"],
    "장미(1차)": ["장미1차", "장미1", "장미2", "장미3", "장미아파트"],
    "현대(1~7차)": ["현대1차", "현대2차", "현대3차", "현대4차", "현대5차", "현대6차", "현대7차", "현대 1차", "압구정현대"],
    "현대(6 7차)": ["현대6차", "현대7차", "현대 6차"],
    "현대(신현대)": ["신현대"],
    "잠실주공(5단지)": ["주공5단지", "잠실주공5", "주공아파트5단지", "주공아파트5"],
}

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def patch():
    complexes = supabase.table("complexes").select("*").execute().data
    target_comps = [c for c in complexes if c["name"] in missing_fixes]
    print(f"Targeting {len(target_comps)} complexes")
    
    for c in target_comps:
        lawd = c["bjd_code"][:5]
        db_dong = c["region"].split()[-1].replace(" ", "")
        print(f"[{c['name']}] LAWD: {lawd}, DONG: {db_dong}")
        
        valid_inserts = []
        # Pull everything from 2014 to 2026!
        year_months = [f"{y}{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if not (y == 2026 and m > 7)]
        
        url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
        for ymd in year_months:
            res = requests.get(url, params={"serviceKey": RTMS_KEY, "LAWD_CD": lawd, "DEAL_YMD": ymd, "numOfRows": 2000})
            if res.status_code != 200: continue
            root = ET.fromstring(res.content)
            
            for item in root.findall(".//item"):
                dealing = item.findtext("dealingGbn", "")
                if "직거래" in dealing: continue
                cdealDay = item.findtext("cdealDay", "").strip()
                if cdealDay: continue
                
                raw_apt = item.findtext("aptNm", "")
                raw_umd = item.findtext("umdNm", "").strip()
                p = format_price(item.findtext("dealAmount"))
                if not raw_apt: continue
                
                if raw_umd != db_dong: continue
                
                raw_apt_clean = raw_apt.replace(" ", "")
                allowed_names = missing_fixes.get(c["name"], [])
                matched = False
                for allowed in allowed_names:
                    al = allowed.replace(" ", "")
                    # CRITICAL FIX: compare clean strings against clean strings
                    if al in raw_apt_clean or raw_apt_clean in al:
                        matched = True
                        break
                        
                if matched:
                    mk = int(round(float(item.findtext("excluUseAr"))))
                    y = item.findtext("dealYear")
                    m = int(item.findtext("dealMonth"))
                    d = int(item.findtext("dealDay"))
                    floor = int(item.findtext("floor", "0"))
                    deal_date = f"{y}-{m:02d}-{d:02d}"
                    valid_inserts.append({
                        "complex_id": c["id"],
                        "match_key_area": mk,
                        "deal_date": deal_date,
                        "deal_price": p,
                        "floor": floor
                    })
        
        print(f" -> Found {len(valid_inserts)} trades (2014-2026)")
        if valid_inserts:
            for i in range(0, len(valid_inserts), 500):
                supabase.table("rtms_transactions").upsert(valid_inserts[i:i+500], on_conflict="complex_id, match_key_area, deal_date, deal_price, floor").execute()

patch()
