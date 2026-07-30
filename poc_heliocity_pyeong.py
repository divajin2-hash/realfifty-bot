# -*- coding: utf-8 -*-
import sys, io
import time
import math
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def list_complex_pyeongs(complex_no="111515", complex_name="송파 헬리오시티"):
    print(f"🚀 {complex_name}({complex_no}) 평형 타입/식별자 매핑 현황 확인\n")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36')
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        found_api_url = None
        target_ptp_info = None

        def handle_response(response):
            nonlocal found_api_url, target_ptp_info
            if found_api_url: return
            url = response.url
            if "complex" in url.lower() or "overview" in url.lower():
                try:
                    data = response.json()
                    data_str = str(data)
                    if "complexPyeongDetailList" in data_str or "pyeongs" in data_str:
                        found_api_url = url
                        target_ptp_info = data
                except:
                    pass

        page.on("response", handle_response)
        
        url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1"
        print(f"👉 네이버 부동산 진입 및 API 감청 중... ({url})")
        
        try:
            page.goto(url, wait_until='networkidle', timeout=15000)
        except:
            pass
            
        time.sleep(2)
        
        if not target_ptp_info:
            print("❌ API 감청 실패. 페이지 파싱을 재시도하거나 모바일 버전을 확인해야 합니다.")
            browser.close()
            return

        ptps = []
        if "pyeongs" in target_ptp_info:
            ptps = target_ptp_info["pyeongs"]
        elif "result" in target_ptp_info and "complexDetail" in target_ptp_info["result"]:
            ptps = target_ptp_info["result"]["complexDetail"].get("complexPyeongDetailList", [])
        elif "complexPyeongDetailList" in target_ptp_info:
            ptps = target_ptp_info["complexPyeongDetailList"]

        print(f"\n✅ 단지 도면 정보 확보 완벽 성공! (총 {len(ptps)}개 타입)")
        print("-" * 75)
        print("전체 개별 평형별 최저호가 추출 시작 (평형 개별 클릭 -> 낮은가격순 정렬)")
        print("-" * 75)

        def parse_korean_price(price_str):
            import re
            clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
            if "억" in clean_str:
                parts = clean_str.split("억")
                eok = int(parts[0]) * 100000000
                digits_only = re.sub(r'[^0-9]', '', parts[1])
                man = int(digits_only) * 10000 if digits_only else 0
                return eok + man
            digits_only = re.sub(r'[^0-9]', '', clean_str)
            return int(digits_only) * 10000 if digits_only else 0

        # 개별 평형 한 개씩 순회
        for p in ptps:
            ptp_no = p.get('pyeongNo') or p.get('ptpNo')
            ptp_nm = p.get('pyeongName') or p.get('pyeongNm')
            ex_area = float(p.get('exclusiveArea', 0))
            
            target_url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&ptpNo={ptp_no}"
            
            target_page = context.new_page()
            try:
                target_page.goto(target_url, wait_until="networkidle", timeout=12000)
                
                # 매물이 하나라도 있는지 확인
                try:
                    target_page.wait_for_selector(".item_inner", timeout=5000)
                except:
                    print(f"[{ptp_nm:<7} / 전용 {ex_area:>5}㎡] ❌ 매물없음")
                    continue
                
                time.sleep(0.5)
                
                # '낮은가격순' 정렬 명시적 클릭
                price_btn = target_page.locator("a[data-nclk='TAA.price']")
                if "is-ascending" not in price_btn.get_attribute("class") or "":
                    price_btn.click(timeout=3000)
                    target_page.wait_for_selector("a[data-nclk='TAA.price'].is-ascending", timeout=4000)
                    time.sleep(1) # 목록 리로딩 확보
                
                cards = target_page.locator(".item_inner").all()[:10]
                found_price = None
                display_price = None
                
                for card in cards:
                    text = card.inner_text()
                    if "지분" in text or "보류지" in text or "경매" in text:
                        continue
                        
                    price_text = card.locator(".price").first.inner_text().strip()
                    price_num = parse_korean_price(price_text)
                    
                    if price_num > 100000000:
                        found_price = price_num
                        display_price = price_text
                        break
                        
                if found_price:
                    print(f"[{ptp_nm:<7} / 전용 {ex_area:>5}㎡] ✅ 최저가: {display_price} ({found_price:,}원)")
                else:
                    print(f"[{ptp_nm:<7} / 전용 {ex_area:>5}㎡] ❌ 매물없음 (또는 정상매물 없음)")
                    
            except Exception as e:
                print(f"[{ptp_nm:<7} / 전용 {ex_area:>5}㎡] ⚠️ 수집 에러 발생")
            finally:
                target_page.close()
            
        browser.close()

if __name__ == "__main__":
    list_complex_pyeongs()
