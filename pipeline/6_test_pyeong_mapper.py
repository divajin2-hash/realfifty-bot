import sys
import io
import json
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def fetch_pyeong_info(p, complex_no, name):
    browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        extra_http_headers={"Referer": "https://new.land.naver.com/complexes/"}
    )
    
    # 먼저 네이버 메인 페이지를 한 번 방문해서 쿠키(NNB 등)를 발급받습니다. (429 에러 방지)
    page = context.new_page()
    page.goto(f"https://new.land.naver.com/complexes/{complex_no}", wait_until="commit", timeout=5000)
    
    print(f"\n======================================")
    print(f"🏢 [{name}] (네이버 단지번호: {complex_no})")
    print(f"======================================")
    
    try:
        # 이후 API 호출
        url = f"https://new.land.naver.com/api/complexes/{complex_no}"
        response = context.request.get(url)
        data = response.json()
        
        pyeongs = data.get("complexPyeongDetailList", [])
        if not pyeongs:
            print("데이터를 찾을 수 없거나 차단됨.")
            return
            
        areas = set()
        for py in pyeongs:
            areas.add(float(py['exclusiveArea']))
        
        areas = sorted(list(areas))
        print(f"🔍 단지 내 발견된 [전체] 전용면적 ㎡ 리스트:\n   {areas}\n")
        
        small_bucket = [a for a in areas if 50 <= a < 70]
        medium_bucket = [a for a in areas if 70 <= a < 90]
        large_bucket = [a for a in areas if 90 <= a]
        
        def closest_to(target, bucket):
            if not bucket: return "없음"
            return min(bucket, key=lambda x: abs(x - target))
            
        print("📊 [AI 평형 자동 매핑 결과]")
        print(f"  👉 소형 (목표 59㎡): {closest_to(59, small_bucket)}㎡ 채택 (탐색범위: {small_bucket})")
        print(f"  👉 국민 (목표 84㎡): {closest_to(84, medium_bucket)}㎡ 채택 (탐색범위: {medium_bucket})")
        print(f"  👉 대형 (대형 대표): {closest_to(114, large_bucket)}㎡ 채택 (탐색범위: {large_bucket})")
        
    except Exception as e:
        print(f"Error fetching {name}: {e}")
    finally:
        browser.close()

if __name__ == "__main__":
    print("🚀 실전 Playwright 쿠키 우회 평형 자동 매핑 가동 중...")
    with sync_playwright() as p:
        fetch_pyeong_info(p, "111515", "송파 헬리오시티")
        fetch_pyeong_info(p, "512", "송파 잠실주공 5단지")
