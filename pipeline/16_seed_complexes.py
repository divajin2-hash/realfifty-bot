import os
import sys
import csv
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# 국토부 실거래가 조회에 필수적인 법정동 코드 매핑 (앞 5자리가 지역 LAWD_CD)
def get_bjd_code(region):
    mapping = {
        # 송파구
        "잠실동": "11710", "가락동": "11710", "신천동": "11710", "방이동": "11710", "문정동": "11710",
        # 강남구
        "개포동": "11680", "대치동": "11680", "압구정동": "11680", "도곡동": "11680", "일원동": "11680",
        # 서초구
        "반포동": "11650", "서초동": "11650", "잠원동": "11650",
        # 강동구
        "고덕동": "11740", "상일동": "11740", "암사동": "11740",
        # 마포구
        "아현동": "11440",
        # 양천구
        "목동": "11470", "신정동": "11470",
        # 용산구
        "서빙고동": "11170", "이촌동": "11170",
        # 영등포구
        "여의도동": "11560",
        # 과천시
        "원문동": "41290",
        # 성남시 수정구
        "신흥동": "41131",
        # 성남시 분당구
        "정자동": "41135"
    }
    
    for dong, cd in mapping.items():
        if dong in region:
            return cd + "00000" # 10자리 규격 맞춤
    return "0000000000"

def seed_db():
    print("🔥 기획자님 제공 Top 50 엑셀 리스트 DB 밀어넣기 시작...")
    
    # 1. 기존 데이터 깔끔하게 초기화 (오류 방지)
    supabase.table("market_stats").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("rtms_transactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("pyeong_stats").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    supabase.table("complexes").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
    
    records = []
    
    with open('data/kb50_list.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bjd = get_bjd_code(row['region'])
            
            # DB 삽입 포맷
            record = {
                "complex_no": row['complex_no'].strip(),
                "name": row['name'].strip(),
                "region": row['region'].strip(),
                "bjd_code": bjd,
                # 기본값
                "total_households": 0,
                "market_cap": 0
            }
            records.append(record)
    
    print(f"   => 추출된 대장단지 총 {len(records)}개. Supabase 삽입 중...")
    
    for r in records:
        supabase.table("complexes").upsert(r, on_conflict="complex_no").execute()
        
    print("✅ 성공적으로 50개 단지의 진짜 정보를 DB에 세팅했습니다!")

if __name__ == "__main__":
    seed_db()
