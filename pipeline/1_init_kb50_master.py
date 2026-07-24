import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
from supabase import create_client, Client

# 1. 환경변수(.env) 로드
load_dotenv()
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

if not URL or not KEY:
    raise ValueError("환경변수 파일에 URL이나 KEY가 없습니다.")

# 2. Supabase DB 연결
supabase: Client = create_client(URL, KEY)

def init_kb50_master():
    print("🚀 KB선도 50 대장주 아파트 마스터 데이터 DB 저장을 시작합니다...")
    
    # 대표 대장주 5개 단지로 정밀하게 세팅 (진짜 네이버 ID 및 법정동 매핑)
    sample_data = [
        {
            "complex_no": "111515",
            "name": "송파 헬리오시티",
            "region": "서울특별시 송파구 가락동",
            "bjd_code": "1171010700",
            "total_households": 9510,
            "market_cap": 0
        },
        {
            "complex_no": "1424",
            "name": "서초 반포자이",
            "region": "서울특별시 서초구 반포동",
            "bjd_code": "1165010700",
            "total_households": 3410,
            "market_cap": 0
        },
        {
            "complex_no": "10586",
            "name": "마포 래미안푸르지오",
            "region": "서울특별시 마포구 아현동",
            "bjd_code": "1144010300",
            "total_households": 3885,
            "market_cap": 0
        },
        {
            "complex_no": "27771",
            "name": "잠실 엘스",
            "region": "서울특별시 송파구 잠실동",
            "bjd_code": "1171010100",
            "total_households": 5678,
            "market_cap": 0
        },
        {
            "complex_no": "95",
            "name": "강남 대치은마",
            "region": "서울특별시 강남구 대치동",
            "bjd_code": "1168010600",
            "total_households": 4424,
            "market_cap": 0
        }
    ]

    # Supabase의 complexes 테이블에 데이터 삽입
    for data in sample_data:
        try:
            # upsert를 사용하면 이미 존재하는 경우 무시하고 덮어씁니다
            res = supabase.table("complexes").upsert(data, on_conflict="complex_no").execute()
            print(f"✅ [{data['name']}] DB 연동 및 저장 성공!")
        except Exception as e:
            print(f"⚠️ [{data['name']}] 저장 중 에러 발생: {e}")

if __name__ == "__main__":
    init_kb50_master()
