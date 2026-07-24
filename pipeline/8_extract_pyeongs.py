import sys
import re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def get_pyeongs_from_list(complex_no, name):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # 필터 없이(기본값) 전체 매물이 나오게 띄움 
        url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&prcSort=asc"
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        try:
            page.wait_for_selector(".item_inner", timeout=10000)
            
            # 스크롤을 5번 정도 내려서 다양한 평형 매물을 로딩
            print(f"[{name}] 매물 스캔 중 (전체 평형 수집)...")
            for _ in range(5):
                page.mouse.wheel(0, 3000)
                page.wait_for_timeout(500)
                
            items = page.locator(".item_inner").all_inner_texts()
            
            areas = set()
            for text in items:
                # 텍스트에서 'XX/84㎡' 형태의 전용면적 추출
                m = re.search(r'/([0-9\.]+)(㎡|m)', text)
                if m:
                    areas.add(float(m.group(1)))
            
            sorted_areas = sorted(list(areas))
            print(f"\n=> 🎯 단지 내 발견된 고유 전용면적 리스트: {sorted_areas}")
            return sorted_areas
            
        except Exception as e:
            print(f"실패: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    get_pyeongs_from_list("111515", "송파 헬리오시티")
    get_pyeongs_from_list("512", "송파 잠실주공 5단지")
