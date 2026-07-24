import os
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = unquote(os.environ.get("RTMS_API_KEY"))
url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"

# The Ultimate Mappings Dict (Only what needs fixing)
fixes = {
    "우성1 2 3차": ["우성아파트", "우성1", "우성 1", "우성2", "우성 2", "우성3", "우성 3"],
    "목동신시가지(9단지)": ["목동신시가지9", "신시가지9"],
    "현대(6 7차)": ["현대6차", "현대7차"],
    "현대(신현대)": ["신현대", "현대9차", "현대11차", "현대12차"],
    "현대(1~7차)": ["현대1차", "현대2차", "현대3차", "현대4차", "현대5차", "현대8차", "현대10차", "현대13차", "현대14차", "현대7차", "현대6차"],
    "래미안힐스테이트고덕": ["고덕래미안힐스테이트", "래미안힐스테이트고덕", "고래힐"],
    "파크뷰": ["파크뷰"],
    "올림픽선수기자촌": ["올림픽선수기자촌"],
    "목동신시가지(13단지)": ["목동신시가지13", "신시가지13"],
    "목동신시가지(14단지)": ["목동신시가지14", "신시가지14"],
    "래미안대치팰리스1단지": ["래미안대치팰리스"],
    "래미안퍼스티지": ["래미안퍼스티지"],
    "신동아": ["신동아"],
    "아시아선수촌": ["아시아선수촌"],
    "신반포(한신4차)": ["신반포4"],
    "고덕그라시움": ["고덕그라시움"],
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
    "한가람": ["한가람"],
    "개포래미안포레스트": ["개포래미안포레스트", "래미안강남포레스트"],
    "아크로리버파크": ["아크로리버파크"],
    "레이크팰리스": ["레이크팰리스"],
    "반포자이": ["반포자이"],
    "래미안원베일리": ["래미안원베일리"],
    "삼풍": ["삼풍"],
    "선경(1 2차)": ["선경1차", "선경2차"],
    "미성(2차)": ["미성", "미성2차"]
}

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def fetch_month(complex_id, lawd_cd, ymd, allowed_names):
    params = {
        "serviceKey": RTMS_KEY,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": ymd,
        "numOfRows": "2000",
        "pageNo": "1"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200: return []
        root = ET.fromstring(res.content)
        insert_buffer = []
        for item in root.findall(".//item"):
            item_apt = item.findtext("aptNm", "")
            if not item_apt: continue
            
            matched = False
            for allowed in allowed_names:
                if allowed in item_apt:
                    matched = True
                    break
            
            if matched:
                p = format_price(item.findtext("dealAmount"))
                mk = int(float(item.findtext("excluUseAr")))
                y = item.findtext("dealYear")
                m = int(item.findtext("dealMonth"))
                d = int(item.findtext("dealDay"))
                floor = int(item.findtext("floor", "0"))
                deal_date = f"{y}-{m:02d}-{d:02d}"
                
                insert_buffer.append({
                    "complex_id": complex_id,
                    "match_key_area": mk,
                    "deal_date": deal_date,
                    "deal_price": p,
                    "floor": floor
                })
        return insert_buffer
    except Exception as e:
        return []

def run_heal():
    complexes = supabase.table("complexes").select("*").execute().data
    
    # 1. 대상 필터링
    target_apts = [c for c in complexes if c["name"] in fixes]
    print(f"🔥 총 {len(target_apts)}개의 오염/누락 단지 발견. 대규모 병렬 복구를 시작합니다...")
    
    # 2. 거래 내역 삭제 (초기화)
    for c in target_apts:
        print(f"[{c['name']}] 기존 오염 데이터 삭제 중...")
        supabase.table("rtms_transactions").delete().eq("complex_id", c["id"]).execute()
        
    year_months = [f"{y}{m:02d}" for y in range(2014, 2027) for m in range(1, 13) if not (y == 2026 and m > 7)]

    # 3. ThreadPool로 병렬 쾌속 스크래핑
    for c in target_apts:
        c_name = c["name"]
        lawd_cd = c["bjd_code"][:5]
        allowed = fixes[c_name]
        
        print(f"\n🚀 [{c_name}] 150개월치 RTMS 병렬 수집 시작... (매칭 키워드: {allowed})")
        
        all_trades = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_ymd = {executor.submit(fetch_month, c["id"], lawd_cd, ymd, allowed): ymd for ymd in year_months}
            
            for future in as_completed(future_to_ymd):
                ymd = future_to_ymd[future]
                res = future.result()
                if res:
                    all_trades.extend(res)
        
        if all_trades:
            # Chunk insert (Supabase limit handles up to 1000 usually)
            chunk_size = 500
            for i in range(0, len(all_trades), chunk_size):
                chunk = all_trades[i:i+chunk_size]
                supabase.table("rtms_transactions").upsert(
                    chunk, on_conflict="complex_id, match_key_area, deal_date, deal_price, floor", ignore_duplicates=True
                ).execute()
            print(f"✅ [{c_name}] 복구 완료: 총 {len(all_trades)}건 적재")
        else:
            print(f"⚠️ [{c_name}] 데이터 없음. (법정동이나 키워드 확인 필요)")
            
    print("\n🎉 모든 오염 단지 복구 완료! JSON 갱신을 수행하세요.")

if __name__ == "__main__":
    run_heal()
