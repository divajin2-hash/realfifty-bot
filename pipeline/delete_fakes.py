import os
import sys
import io
from supabase import create_client, Client
from dotenv import load_dotenv

# 윈도우 cp949 인코딩 에러(이모지 깨짐) 완벽 방지!
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("Supabase 환경 변수가 없습니다.")
    sys.exit(1)

supabase: Client = create_client(url, key)

def delete_dummies():
    print("🔥 가짜 데이터(부천, 파주) 삭제 스크립트 가동 중...")
    
    # 1424, 10586 번호 삭제
    dummy_nos = ["1424", "10586"]
    
    # 해당 단지 찾기
    for d_no in dummy_nos:
        res = supabase.table("complexes").select("id").eq("complex_no", d_no).execute().data
        if res:
            cid = res[0]["id"]
            # 자식 테이블 기록 먼저 지우기
            supabase.table("market_stats").delete().eq("complex_id", cid).execute()
            # 단지 지우기
            supabase.table("complexes").delete().eq("complex_no", d_no).execute()
            print(f"✅ 네이버 단지코드 {d_no} 완벽 삭제 완료!")
            
    print("✨ 더미 데이터 청소 완료! 이제 진짜 강남/서울 대장주 5개만 남았습니다.")

if __name__ == "__main__":
    delete_dummies()
