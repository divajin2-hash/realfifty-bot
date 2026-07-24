import os
import sys
import io
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

# 프로토타입/MVP를 위해 가장 인기있는 5개 단지의 실제 84㎡ '역대 최고가(ATH)'와 '기록 시기'를 정확히 세팅해 둡니다.
# (RTMS API로 전체 내역을 뒤지려면 5년치 월별 루프를 돌아야 하므로 초기 1회 배치 작업이 필요합니다.)
REAL_ATH_DATA = {
    "111515": {"name": "송파 헬리오시티", "highest_price": 3140000000, "highest_date": "2026-01-01"},     
    "1424": {"name": "서초 반포자이", "highest_price": 3900000000, "highest_date": "2022-05-01"},        
    "10586": {"name": "마포 래미안푸르지오", "highest_price": 1950000000, "highest_date": "2021-09-01"},     
    "27771": {"name": "잠실 엘스", "highest_price": 2700000000, "highest_date": "2021-10-01"},             
    "95": {"name": "강남 대치은마", "highest_price": 2820000000, "highest_date": "2021-11-01"},            
}

def analyze_and_update_mdd():
    print("🧠 [데이터 분석 봇] 최고가 기반 MDD(하락률) 산출 작업을 시작합니다...")
    
    # 1. 아파트 단지 정보 가져오기
    complexes_data = supabase.table("complexes").select("*").execute().data
    
    for c in complexes_data:
        comp_id = c["id"]
        comp_no = c["complex_no"]
        name = c["name"]
        
        # 임의로 부여된 더미 번호 처리 방지
        if comp_no not in REAL_ATH_DATA:
            continue
            
        highest_price = REAL_ATH_DATA[comp_no]["highest_price"]
        highest_date = REAL_ATH_DATA[comp_no]["highest_date"]
        
        # 2. 방금 네이버에서 수집한 '현재 최저호가' 가져오기 (가장 가격이 낮은 1건)
        listings_res = supabase.table("listings").select("price, source_url").eq("complex_id", comp_id).order("price", desc=False).limit(1).execute()
        
        if not listings_res.data:
            print(f"⚠️ [{name}] 현재 저장된 매매 호가가 없습니다. (계산 스킵)")
            continue
            
        current_lowest_price = listings_res.data[0]["price"]
        
        # 3. MDD (최고가 대비 하락률) 계산
        # 공식: ((현재호가 - 최고가) / 최고가) * 100
        mdd_rate = ((current_lowest_price - highest_price) / highest_price) * 100.0
        mdd_rate = round(mdd_rate, 2)
        
        print(f"\n📊 [{name}] MDD 분석 결과")
        print(f"   - 역대 최고가: {highest_price:,}원 ({highest_date})")
        print(f"   - 현재 최저가: {current_lowest_price:,}원")
        print(f"   - MDD (하락률): {mdd_rate}%")
        
        # 4. market_stats 테이블에 저장 (upsert)
        stat_data = {
            "complex_id": comp_id,
            "highest_price": highest_price,
            "highest_date": highest_date,
            "latest_price": current_lowest_price, # 최근 실거래가를 모방하여 최저호가로 임시 세팅하거나 None으로 둠 (현재는 호가 기준 MDD)
            "current_lowest_price": current_lowest_price,
            "mdd_rate": mdd_rate
        }
        
        try:
            # 기존 데이터가 있으면 삭제 후 삽입 (간편한 Upsert 대용)
            supabase.table("market_stats").delete().eq("complex_id", comp_id).execute()
            supabase.table("market_stats").insert(stat_data).execute()
            print("   ✅ 통계 DB 저장 완료!")
        except Exception as e:
            print(f"   ❌ DB 업로드 실패: {e}")

if __name__ == "__main__":
    analyze_and_update_mdd()
