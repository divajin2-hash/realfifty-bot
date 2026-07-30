# -*- coding: utf-8 -*-
import sys
import io
import time
import re
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def run_heliocity_safe_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36')
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        print("==========================================================")
        print("🏢 헬리오시티(111515) 전 평형 실시간 최저가 검증 (DOM 파싱판)")
        print("==========================================================\n")
        
        # 1. 헬리오시티 페이지 정상 진입
        url = 'https://new.land.naver.com/complexes/111515?ms=37.497554,127.10649,17&a=APT&b=A1&e=RETAIL'
        page.goto(url, wait_until='networkidle', timeout=15000)
        time.sleep(3)
        
        # 2. 면적 드롭다운 탭 열고 상세 정보 클릭하기
        print("1️⃣ 화면에서 평형(면적) 정보 파싱 시작...")
        
        # '전체면적' 드롭다운 버튼 열기 시도 (여러 셀렉터 대응)
        d_btns = page.locator("button.complex_feature_area").all()
        if not d_btns:
            print("❌ 전체면적 드롭다운 버튼을 찾을 수 없습니다.")
            return
            
        d_btns[0].click()
        time.sleep(1) # 모달 열리는 시간 대기
        
        # 3. 면적 모달 안에 있는 평형 정보 뽑아내기
        area_items = page.locator(".complex_area_item").all()
        if not area_items:
            # UI가 변경된 경우 체크박스로 평면도를 보여주는 팝업 버튼 클릭 시도
            page.locator("button.btn_area_detail").click(timeout=3000)
            time.sleep(2)
            area_items = page.locator(".area_item").all()

        pyeongs = []
        html_eval = page.evaluate("""() => {
            // 네이버 UI에 뿌려진 팝업 내부의 라디오 혹은 체크박스 엘리먼트 순회
            let results = [];
            // '면적팝업' 형태일 때
            document.querySelectorAll('.area_list .area_item, .dropdown_list .dropdown_item').forEach(el => {
                let name = el.innerText.trim();
                let input = el.querySelector('input');
                let value = input ? input.value : null; // ptpNo 형태일 확률 높음
                if(value && name) {
                    results.push({name: name, val: value});
                }
            });
            return results;
        }""")
        
        if html_eval:
             print(f"✅ 일반 UI에서 {len(html_eval)}개의 평형 리스트를 추출했습니다: {html_eval[:3]}...")
        else:
             print("⚠️ 면적 리스트 파싱 로직 2차 우회 시도...")
             # URL에 ptpNo를 비워서 강제로 서버 HTML 응답을 캐시해봅니다.
             pass

        print("----------------------------------------------------------")
        print("결과가 제대로 나오지 않아, 방어 로직이 필요합니다. 스크립트 재조정 후 진행하겠습니다.")
        browser.close()

if __name__ == "__main__":
    run_heliocity_safe_test()
