import os
import sys
import json
import math
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv("pipeline/.env")

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_mdd_bridge():
    print("▶ 네이버 최저호가(JSON) ↔ 국토부 최고가(DB) 매칭 및 MDD 결산 시작")
    target_date = datetime.now().strftime('%Y-%m-%d')
    json_path = f"pipeline/raw_daily_asks_{target_date}.json"
    
    if not os.path.exists(json_path):
        print(f"❌ 대기 중: 아직 오늘치 네이버 수집 파일({json_path})이 생성되지 않았습니다.")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        daily_asks = json.load(f)
        
    print(f"✅ 네이버 최저호가 {len(daily_asks)}건 로드 완료.")
    
    # 1. 아파트 단지 정보 매핑 (uuid -> name)
    complexes = supabase.table("complexes").select("id, complex_no").execute().data
    cx_map_id = {str(c["complex_no"]): c["id"] for c in complexes}
    
    # 2. Main Page용 '대표 평형(정수 그룹)' 최저호가 집계
    # 84.98, 84.96 등 모든 84점대 면적들 중 '가장 저렴한 놈' 하나를 대표 84 최저호가로 선출!
    grouped_asks = {}
    for ask in daily_asks:
        c_no = ask.get("complex_no")
        if not c_no: continue
        cid = cx_map_id.get(c_no)
        if not cid: continue
        
        # 소수점 면적을 반올림하여 DB의 match_key_area와 호환되도록 평탄화
        ex_area = ask.get("exclusive_area", 0)
        match_key = int(round(ex_area))
        
        # 특정 단지의 match_key(평형) 중 절대적 최저호가 발굴
        price = ask.get("lowest_ask", 0)
        if price == 0: continue
        
        node_key = f"{cid}_{match_key}"
        if node_key not in grouped_asks or price < grouped_asks[node_key]["price"]:
            grouped_asks[node_key] = {
                "cid": cid,
                "match_key_area": match_key,
                "price": price,
                "ptp_no": ask.get("ptp_no", "0"),
                "pyeong_name": ask.get("ptp_name", f"{match_key}㎡")
            }
            
    # 3. 국토부 실거래 DB에서 대표 평형별 '최고가(ATH)' 추출
    print(f"✅ 대표 평형 그룹핑 완료. (총 {len(grouped_asks)}개 대표 평형 그룹)")
    
    # Fetch all rtms trades to find max (could be heavy, but it's only ~100k rows)
    # limit is 1000, so we use pagination
    all_trades = []
    offset = 0
    limit = 1000
    while True:
        res = supabase.table("rtms_transactions").select("complex_id, match_key_area, deal_price, deal_date").range(offset, offset+limit-1).execute().data
        if not res: break
        all_trades.extend(res)
        if len(res) < limit: break
        offset += limit
        
    grouped_ath = {}
    for t in all_trades:
        key = f"{t['complex_id']}_{t['match_key_area']}"
        if key not in grouped_ath or t["deal_price"] > grouped_ath[key]["price"]:
            grouped_ath[key] = {
                "price": t["deal_price"],
                "date": t["deal_date"]
            }
            
    # 4. MDD 결합 및 pyeong_stats 테이블 Upsert
    stats_to_insert = []
    
    # Iterate over our aggregated Naver asks
    for node_key, ask_data in grouped_asks.items():
        ath = grouped_ath.get(node_key)
        
        # 최고가가 없는 평형(거래내역 전무)일 경우 MDD 계산 불가
        if not ath:
            continue
            
        ath_price = ath["price"]
        current_ask = ask_data["price"]
        
        if ath_price > 0:
            mdd = round(((current_ask - ath_price) / ath_price) * 100, 2)
        else:
            mdd = 0
            
        stats_to_insert.append({
            "complex_id": ask_data["cid"],
            "pyeong_name": ask_data["pyeong_name"],
            "naver_ptp_no": ask_data["ptp_no"],
            "match_key_area": ask_data["match_key_area"],
            "current_lowest_ask": current_ask,
            "highest_deal_price": ath_price,
            "highest_deal_date": ath["date"],
            "mdd_rate": mdd
        })
        
    print(f"✅ 최종 MDD 산출 완료: {len(stats_to_insert)}개 평형 블록 업데이트 준비.")
    
    # 5. DB pyeong_stats 테이블 업데이트
    # ⚠️ 먼저 기존 레거시 데이터를 완전히 삭제하여, 구형 스크래퍼가 남긴 오염 데이터 제거
    supabase.table("pyeong_stats").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    print("🗑️ 기존 pyeong_stats 전체 초기화 완료. 신규 데이터로 교체합니다.")
    
    if stats_to_insert:
        chunk_size = 500
        for i in range(0, len(stats_to_insert), chunk_size):
            supabase.table("pyeong_stats").upsert(stats_to_insert[i:i+chunk_size], on_conflict="complex_id, match_key_area").execute()
            
    print("🎉 Main 페이지용 대표 평형 MDD 업데이트(pyeong_stats) 성공!")

if __name__ == "__main__":
    run_mdd_bridge()
