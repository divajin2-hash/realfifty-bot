import os
import sys
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
    print("❌ 에러: .env 정보가 없습니다.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

aliases = {
    "우성1 2 3차": ["우성아파트", "우성1", "우성 1", "우성2", "우성 2", "우성3", "우성 3"],
    "목동신시가지(9단지)": ["목동신시가지9", "신시가지9"],
    "잠실주공(5단지)": ["주공아파트5단지", "잠실주공5단지", "잠실주공5", "주공5단지", "주공5"],
    "현대(1~5차)": ["현대1", "현대2", "현대3", "현대4", "현대5", "현대(1,2차)", "현대(3차)", "현대(4차)", "현대(5차)"],
    "고덕힐스테이트고덕": ["고덕래미안힐스테이트", "래미안힐스테이트고덕", "고래힐", "고덕래미안힐스테이트"],
    "올림픽선수기자촌": ["올림픽선수기자촌", "올림픽선수기자촌1단지", "올림픽선수기자촌2단지", "올림픽선수기자촌3단지"],
    "목동신시가지(13단지)": ["목동신시가지13", "신시가지13"],
    "목동신시가지(14단지)": ["목동신시가지14", "신시가지14"],
    "디에이치퍼스티어아이파크": ["디에이치퍼스티어아이파크", "개포주공1단지"],
    "래미안대치팰리스1단지": ["래미안대치팰리스"],
    "마포래미안푸르지오": ["마포래미안푸르지오1단지", "마포래미안푸르지오2단지", "마포래미안푸르지오3단지", "마포래미안푸르지오4단지"]
}

def clean_name(n):
    return n.replace("(", "").replace(")", "").replace(" ", "").strip()

def is_matched(api_name, db_name):
    clean_api = clean_name(api_name)
    clean_db = clean_name(db_name)
    if clean_api == clean_db: return True
    for original, alias_list in aliases.items():
        if clean_db == clean_name(original):
            for al in alias_list:
                if clean_api == clean_name(al):
                    return True
    return False

def run_daily_rtms_crawler():
    print("▶ 국토부 실거래가 통합 수집기 가동 (순수 중개거래 & 소수점 면적 & 별명)")
    complexes = supabase.table("complexes").select("*").execute().data
    
    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    safe_key = unquote(RTMS_KEY)
    
    now = datetime.now()
    last_month_dt = (now.replace(day=1) - timedelta(days=1))
    target_ymds = [last_month_dt.strftime("%Y%m"), now.strftime("%Y%m")]
    
    # 2 endpoints: General Apt + Rights
    endpoints = [
        "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev",
        "http://apis.data.go.kr/1613000/RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade"
    ]
    
    total_inserted = 0
    
    for ymd in target_ymds:
        print(f"\n✅ 조회 연월: {ymd}")
        
        for lawd_cd, apts in lawd_map.items():
            for ep in endpoints:
                params = {
                    "serviceKey": safe_key,
                    "LAWD_CD": lawd_cd,
                    "DEAL_YMD": ymd,
                    "numOfRows": "2000",
                    "pageNo": "1"
                }
                
                try:
                    res = requests.get(ep, params=params, timeout=15)
                    if res.status_code != 200: continue
                    root = ET.fromstring(res.content)
                    
                    for item in root.findall(".//item"):
                        deal_type = item.findtext("dealingGbn", "")
                        
                        # [핵심] 직거래 배제 (중개거래만 허용하거나 직거래가 아닌 것들만)
                        if "직거래" in deal_type: 
                            continue
                            
                        item_apt = item.findtext("aptNm", "")
                        if not item_apt: continue
                        
                        for c in apts:
                            if is_matched(item_apt, c["name"]):
                                price = format_price(item.findtext("dealAmount"))
                                area_exact = float(item.findtext("excluUseAr"))
                                mk_area = int(round(area_exact))
                                floor = int(item.findtext("floor", "0"))
                                date = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
                                
                                row = {
                                    "complex_id": c["id"],
                                    "match_key_area": mk_area,
                                    "deal_date": date,
                                    "deal_price": price,
                                    "floor": floor,
                                    "transaction_type": deal_type,
                                    "exclusive_area_exact": area_exact
                                }
                                
                                # Check duplicate before upserting (optional but good for clean DB)
                                existing = supabase.table("rtms_transactions") \
                                    .select("id") \
                                    .eq("complex_id", row["complex_id"]) \
                                    .eq("deal_date", row["deal_date"]) \
                                    .eq("deal_price", row["deal_price"]) \
                                    .eq("floor", row["floor"]) \
                                    .eq("exclusive_area_exact", row["exclusive_area_exact"]) \
                                    .execute()
                                
                                if not existing.data:
                                    supabase.table("rtms_transactions").insert(row).execute()
                                    total_inserted += 1
                                break
                except Exception as e:
                    pass
                    
    print(f"\n🎉 통합 수집 완료. 총 {total_inserted}건의 신규 실거래가(중개거래 한정) 적재됨.")

if __name__ == "__main__":
    run_daily_rtms_crawler()
