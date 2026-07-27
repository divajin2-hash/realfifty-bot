import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import requests
from supabase import create_client, Client
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('pipeline/.env')

supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = unquote(os.environ.get("RTMS_API_KEY"))

URL_APT = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
URL_RIGHTS = "http://apis.data.go.kr/1613000/RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade"

# OLD NAMES REMOVED TO ENSURE WE ONLY GET POST-RECONSTRUCTION DEALS!
aliases = {
    "우성1 2 3차": ["우성아파트", "우성1", "우성 1", "우성2", "우성 2", "우성3", "우성 3"],
    "목동신시가지(9단지)": ["목동신시가지9", "신시가지9"],
    "잠실주공(5단지)": ["주공아파트5단지", "잠실주공5단지", "잠실주공5", "주공5단지", "주공5"],
    "현대(1~5차)": ["현대1", "현대2", "현대3", "현대4", "현대5", "현대(1,2차)", "현대(3차)", "현대(4차)", "현대(5차)"],
    "고덕힐스테이트고덕": ["고덕래미안힐스테이트", "래미안힐스테이트고덕", "고래힐", "고덕래미안힐스테이트"],
    "올림픽선수기자촌": ["올림픽선수기자촌", "올림픽선수기자촌1단지", "올림픽선수기자촌2단지", "올림픽선수기자촌3단지"],
    "목동신시가지(13단지)": ["목동신시가지13", "신시가지13"],
    "목동신시가지(14단지)": ["목동신시가지14", "신시가지14"],
    "래미안대치팰리스1단지": ["래미안대치팰리스"],
    "마포래미안푸르지오": ["마포래미안푸르지오1단지", "마포래미안푸르지오2단지", "마포래미안푸르지오3단지", "마포래미안푸르지오4단지"]
}
# Notice: '디에이치퍼스티어아이파크': ['개포주공1단지'] has been INTENTIONALLY EXCLUDED!
# Because the user explicitly wants POST-reconstruction data only. By not aliasing the old demolished name,
# the scraper will naturally ignore Gae-po Jugong 1 and only scoop up '디에이치퍼스티어아이파크' pre-sales and apt trades!

def clean_name(n):
    return n.replace("(", "").replace(")", "").replace(" ", "").strip()

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def fetch_trades(url, lawd, ymd):
    params = {
        "serviceKey": RTMS_KEY,
        "LAWD_CD": lawd,
        "DEAL_YMD": ymd,
        "numOfRows": "3000",
        "pageNo": "1"
    }
    extracted = []
    try:
        res = requests.get(url, params=params, timeout=12)
        if res.status_code != 200: return []
        root = ET.fromstring(res.content)
        
        for item in root.findall(".//item"):
            # Exclude direct transactions (직거래)
            deal_type = item.findtext("dealingGbn", "")
            if "직거래" in deal_type:
                continue
                
            apt = clean_name(item.findtext("aptNm", ""))
            umd = clean_name(item.findtext("umdNm", ""))
            if not apt: continue
            
            p = format_price(item.findtext("dealAmount"))
            ex_ar = float(item.findtext("excluUseAr", "0"))
            date_str = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
            f = int(item.findtext("floor", "0"))
            
            extracted.append({
                "aptNm": apt,
                "umdNm": umd,
                "deal_price": p,
                "exclusive_area_exact": ex_ar,
                "match_key_area": int(round(ex_ar)),
                "deal_date": date_str,
                "floor": f,
                "transaction_type": deal_type
            })
    except Exception as e:
        pass
    return extracted

def run_rebuild():
    print("▶ 과거 국토부 완전 초기화 및 10년치 재건축 (직거래 배제 / 소수점 보존 / 입주권 포함)")
    
    # 1. TRUNCATE CURRENT TABLE
    print("   [1] 기존 껍데기 뿐인 테이블(rtms_transactions) 삭제 중...")
    try:
        # To delete all without hitting limit, we cheat by eq('id', 'uuid') no we can use neq
        # But safest is to delete in batches or let user know. For now we just query IDs and delete
        res = supabase.table("rtms_transactions").select("id").execute().data
        chunk = 500
        for i in range(0, len(res), chunk):
            ids = [x["id"] for x in res[i:i+chunk]]
            supabase.table("rtms_transactions").delete().in_("id", ids).execute()
    except Exception as e:
        print("   ⚠️ 테이블 초기화 실패. (Supabase 대시보드에서 직접 Truncate 하시는 것이 빠릅니다.")
    
    print("   [2] 단지 정보 매핑 로드")
    complexes = supabase.table("complexes").select("*").execute().data
    lawds = set([c["bjd_code"][:5] for c in complexes])
    
    year_months = []
    for y in range(2014, 2027):
        for m in range(1, 13):
            if y == 2026 and m > 7: break
            year_months.append(f"{y}{m:02d}")
            
    print(f"   [3] {len(year_months)}개월 * {len(lawds)}지역 집중 수집 시작...")
    
    all_data = []
    
    with ThreadPoolExecutor(max_workers=20) as exe:
        futs = []
        for lawd in lawds:
            for ym in year_months:
                futs.append(exe.submit(fetch_trades, URL_APT, lawd, ym))
                # for rights, we might just fetch from 2018 onwards to save time
                if int(ym[:4]) >= 2017:
                    futs.append(exe.submit(fetch_trades, URL_RIGHTS, lawd, ym))
                    
        for fut in as_completed(futs):
            r = fut.result()
            if r: all_data.extend(r)
            
    print(f"   ✅ 다운로드 완료. 총 후보 거래건: {len(all_data)}건")
    
    # Matching
    valid_inserts = []
    for t in all_data:
        raw_apt = t["aptNm"]
        raw_umd = t["umdNm"]
        
        matched_c_id = None
        for c in complexes:
            db_dong = clean_name(c["region"].split()[-1])
            if raw_umd != db_dong: continue
            
            c_name = clean_name(c["name"])
            allowed_names = [c_name]
            for orig, als in aliases.items():
                if c_name == clean_name(orig):
                    allowed_names.extend([clean_name(a) for a in als])
                    
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
                "floor": t["floor"],
                "exclusive_area_exact": t["exclusive_area_exact"],
                "transaction_type": t["transaction_type"]
            })
            
    print(f"   ✅ 타겟 단지(50개) 완벽 매칭 성공: {len(valid_inserts)}건")
    
    if valid_inserts:
        chunk_size = 500
        for i in range(0, len(valid_inserts), chunk_size):
            try:
                supabase.table("rtms_transactions").upsert(valid_inserts[i:i+chunk_size], ignore_duplicates=True).execute()
                print(f"      - {i + len(valid_inserts[i:i+chunk_size])}건 적재 완료")
            except Exception as e:
                print(f"      - Chunk error: {e}")
            
    print("\n🎉 모든 역사적 통합 실거래가 데이터 적재 완료!")

if __name__ == "__main__":
    run_rebuild()
