# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import time
from playwright.sync_api import sync_playwright

def find_hidden_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36')
        page = ctx.new_page()

        print("🕵️ 네이버 부동산 백도어(API) 통신망 전체 감청 시작...\n")

        found_api_url = None
        target_ptp_info = None

        def handle_response(response):
            nonlocal found_api_url, target_ptp_info
            # 이미 찾았으면 무시
            if found_api_url: return
            
            # json으로 응답하는 모든 네트워크 요청 검사
            url = response.url
            if "complex" in url.lower() or "article" in url.lower() or "detail" in url.lower():
                try:
                    data = response.json()
                    # 응답 JSON 안에 'complexPyeongDetailList' 나 'ptpNo' 같은 키워드가 있는지 무차별 검사
                    data_str = str(data)
                    if "complexPyeongDetailList" in data_str or "exclusiveArea" in data_str:
                        print(f"🚨 찾았습니다! 진짜 평형 API 주소: {url}")
                        found_api_url = url
                        target_ptp_info = data
                except:
                    pass

        page.on("response", handle_response)

        # 헬리오시티 접속
        print("👉 헬리오시티 렌더링 중... (10초간 통신 감청)")
        page.goto('https://new.land.naver.com/complexes/111515?ms=37.497554,127.10649,17&a=APT&b=A1&e=RETAIL', wait_until='networkidle')
        
        # 화면 내 버튼 등도 눌러보면서 API 통신을 유도
        time.sleep(3)
        try:
            page.locator("button.complex_feature_area").first.click(timeout=3000)
            time.sleep(1)
        except:
            pass
            
        time.sleep(5)
        
        if target_ptp_info:
            print("\n✅ 은닉된 평형 정보를 성공적으로 탈환했습니다.")
            
            # 파싱 구조 확인
            try:
                if "pyeongs" in target_ptp_info:
                    ptps = target_ptp_info["pyeongs"]
                elif "result" in target_ptp_info and "complexDetail" in target_ptp_info["result"]:
                    ptps = target_ptp_info["result"]["complexDetail"].get("complexPyeongDetailList", [])
                elif "complexPyeongDetailList" in target_ptp_info:
                    ptps = target_ptp_info["complexPyeongDetailList"]
                else:
                    ptps = []
                     
                print(f"총 {len(ptps)}개 타입 확인.")
                for p in ptps[:5]:
                    ptp_no = p.get('pyeongNo') or p.get('ptpNo')
                    ptp_nm = p.get('pyeongName') or p.get('pyeongNm')
                    print(f" -> {ptp_nm}: 전용 {p.get('exclusiveArea')}㎡ (ptpNo={ptp_no})")
            except Exception as e:
                import json
                print("파싱 트리 구조가 다릅니다:", str(e))
                with open("api_dump.json", "w", encoding="utf-8") as f:
                    json.dump(target_ptp_info, f, ensure_ascii=False, indent=2)
                print("API 구조를 api_dump.json 파일에 저장했습니다.")
        else:
            print("❌ 감청 실패. 네이버가 API 통신이 아닌 웹소켓이나 완전히 다른 방식으로 데이터를 렌더링하고 있습니다.")

        browser.close()

if __name__ == "__main__":
    find_hidden_api()
