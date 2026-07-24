import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test_kbland():
    # 헬리오시티 KB 단지 번호: 32148
    kb_id = "32148"
    url = f"https://kbland.kr/c/{kb_id}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        
        print("KB 부동산 접속 중...")
        page.goto(url)
        page.wait_for_timeout(3000)
        
        # KB랜드는 내부에 윈도우 객체로 데이터를 가지고 있을 확률이 높습니다.
        # 혹은 DOM 내 텍스트를 바로 가져옵니다.
        try:
            body_text = page.locator("body").inner_text()
            print("성공적으로 화면을 로드했습니다. 길이:", len(body_text))
            
            # 버튼 중 '평' 이 들어간 것들 전부 추출
            # KB랜드는 보통 '18평', '25평', '33평' 등으로 명확히 표기합니다.
            import re
            pyeongs = set(re.findall(r'([0-9]+)평\b', body_text))
            print("🔥 바탕 화면에서 추출된 '평' 리스트:", sorted([int(x) for x in pyeongs]))
            
        except Exception as e:
            print("에러:", e)
            
        browser.close()

test_kbland()
