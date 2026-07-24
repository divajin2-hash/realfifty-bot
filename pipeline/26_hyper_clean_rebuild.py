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

fixes = {
    "우성1 2 3차": ["우성아파트", "우성1", "우성 1", "우성2", "우성 2", "우성3", "우성 3"],
    "목동신시가지(9단지)": ["목동신시가지9", "신시가지9"],
    "주공(6 7단지)": ["주공6단지", "주공7단지"],
    "주공(구현대)": ["구현대", "주공9단지", "주공11단지", "주공12단지"],
    "주공(1~7단지)": ["주공1단지", "주공2단지", "주공3단지", "주공4단지", "주공5단지", "주공8단지", "주공10단지", "주공13단지", "주공14단지"],
    "고덕힐스테이트고덕": ["고덕아남힐스테이트", "아남힐스테이트고덕", "고래힐", "고덕래미안힐스테이트"],
    "대림이선경기촌": ["대림이선경기촌", "대림이편한세상"],
    "목동신시가지(13단지)": ["목동신시가지13", "신시가지13"],
    "목동신시가지(14단지)": ["목동신시가지14", "신시가지14"],
    "디에이치퍼스티어아이파크": ["디에이치퍼스티어아이파크", "개포주공1단지"],
    "래미안대치팰리스1단지": ["래미안대치팰리스"],
    "신반포(신신4차)": ["신반포"],
    "목동신시가지(1단지)": ["목동신시가지1", "신시가지1"],
    "목동신시가지(2단지)": ["목동신시가지2", "신시가지2"],
    "목동신시가지(3단지)": ["목동신시가지3", "신시가지3"],
    "목동신시가지(4단지)": ["목동신시가지4", "신시가지4"],
    "목동신시가지(5단지)": ["목동신시가지5", "신시가지5"],
    "목동신시가지(6단지)": ["목동신시가지6", "신시가지6"],
    "목동신시가지(7단지)": ["목동신시가지7", "신시가지7"],
    "타워팰리스(1차)": ["타워팰리스1"],
    "타워팰리스(2차)": ["타워팰리스2"],
    "타워팰리스(3차)": ["타워팰리스3"],
    "개포우성포레스": ["개포우성포레스", "우성강포레스", "우성"],
    "래미안원베일리": ["래미안원베일리", "신반포3차", "경남"],
    "우경(1 2차)": ["우경1차", "우경2차"],
    "미성(2차)": ["미성", "미성2차"],
    "선경(1 2차)": ["선경1차", "선경2차", "선경"],
    "신반포(한신4차)": ["신반포4차", "한신4차", "한신4"],
    "장미(1차)": ["장미1차", "장미1", "장미2", "장미3", "장미아파트"],
    "현대(1~7차)": ["현대1차", "현대2차", "현대3차", "현대4차", "현대5차", "현대6차", "현대7차", "현대 1차", "압구정현대", "현대"],
    "현대(6 7차)": ["현대6차", "현대7차", "현대 6차"],
    "현대(신현대)": ["신현대"],
    "잠실주공(5단지)": ["주공5단지", "잠실주공5", "주공아파트 5"],
}

URL_APT = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
URL_RIGHTS = "http://apis.data.go.kr/1613000/RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade"

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def fetch_pure_trades(url, lawd_cd, ymd, is_rights=False):
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
            
            # Canceled Trade Check
            cdealDay = item.findtext("cdealDay", "").strip()
            if cdealDay: 
                continue # exclude cancelled trades!
                
            apt = item.findtext("aptNm", "")
            umd = item.findtext("umdNm", "").strip()
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
                "umdNm": umd.replace(" ", ""),
                "match_key_area": mk,
                "deal_date": deal_date,
                "deal_price": p,
                "floor": floor
            })
        return trades
    except Exception as e:
        return []

def run_rebuild():
    complexes = supabase.table("complexes").select("*").execute().data
    lawd_map = {}
    for c in complexes:
        lawd = c["bjd_code"][:5]
        if lawd not in lawd_map: lawd_map[lawd] = []
        lawd_map[lawd].append(c)
        
    year_months = [f"{y}{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if not (y == 2026 and m > 7)]

    print(f"Wiping existing rtms_transactions...")
    for c in complexes:
        supabase.table("rtms_transactions").delete().eq("complex_id", c["id"]).execute()

    print("Rebuilding PURE trades WITH ALIAS + DONG MATCHING + NO CANCELLED...")
    
    total = 0
    for lawd, comps in lawd_map.items():
        print(f"Processing LAWD {lawd}...")
        all_apt = []
        all_rights = []
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            fut_apt = {executor.submit(fetch_pure_trades, URL_APT, lawd, ymd, False): ymd for ymd in year_months}
            for fut in as_completed(fut_apt):
                r = fut.result()
                if r: all_apt.extend(r)
                
        recent_ymds = [ymd for ymd in year_months if int(ymd[:4]) >= 2023] # changed from 2020 to 2023 for speed
        with ThreadPoolExecutor(max_workers=10) as executor:
            fut_rights = {executor.submit(fetch_pure_trades, URL_RIGHTS, lawd, ymd, True): ymd for ymd in recent_ymds}
            for fut in as_completed(fut_rights):
                r = fut.result()
                if r: all_rights.extend(r)
                
        merged = all_apt + all_rights
        
        valid_inserts = []
        for t in merged:
            raw_apt = t["aptNm"]
            raw_umd = t["umdNm"]
            
            matched_c_id = None
            for c in comps:
                # 1. STRICT LEGAL DONG (법정동) CHECK
                # "서울특별시 강남구 대치동" -> "대치동"
                db_dong = c["region"].split()[-1].replace(" ", "")
                if raw_umd != db_dong:
                    continue # Not the same dong! Skip entirely!
                
                # 2. NAME ALIAS CHECK
                c_name = c["name"]
                db_name = c_name.replace(" ", "")
                allowed_names = fixes.get(c_name, [db_name])
                
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
    run_rebuild()
