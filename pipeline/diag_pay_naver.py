"""
diag_pay_naver.py
new.m.pay.naver.com 에서 타워팰리스 1차 112A vs 112B 확인
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

# 타워팰리스 1차 
# new.m.pay.naver.com 에서 사용하는 단지 ID 확인 필요
# 기존 nid=634, ptpNo=7(112A), ptpNo=8(112B)

NID = "634"
TEST_PTPS = [("112A", "7"), ("112B", "8")]

def get_type_tabs(page):
    """시세/실거래가 패널의 타입 탭 목록 수집"""
    tabs = page.evaluate("""
        () => Array.from(document.querySelectorAll('a, button, li'))
            .filter(el => {
                const cls = el.className || '';
                const txt = (el.innerText || '').trim();
                return txt.match(/\\d+[AB]?㎡/) && txt.length < 15;
            })
            .map(el => ({
                tag: el.tagName,
                cls: el.className || '',
                txt: (el.innerText||'').trim(),
                id: el.id || ''
            }))
    """)
    return tabs

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
            viewport={"width": 390, "height": 844},
        )
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # URL 패턴 테스트: new.m.pay.naver.com
        # 실제 사용자 화면에서 사용되는 URL 형식
        urls_to_try = [
            f"https://new.m.pay.naver.com/realty/complexes/{NID}?ptpNo=7",
            f"https://m.land.naver.com/complex/info/{NID}?ptpNo=7",
            f"https://new.land.naver.com/complexes/{NID}?a=APT&b=A1&ptpNo=7",
        ]

        for url in urls_to_try:
            print(f"\n테스트 URL: {url}")
            page = ctx.new_page()
            try:
                page.goto(url, wait_until='domcontentloaded', timeout=20000)
                time.sleep(3)
                
                # 112 포함 요소 확인
                tabs = get_type_tabs(page)
                print(f"  타입탭: {[t['txt'] for t in tabs[:15]]}")
                
                # 현재 URL
                current_url = page.url
                print(f"  현재URL: {current_url}")
                
                # 제목
                title = page.title()
                print(f"  제목: {title}")

            except Exception as e:
                print(f"  오류: {e}")
            finally:
                page.close()

        print("\n=== 정상 URL로 패널 탐색 ===")
        # new.land.naver.com 에서 112A/112B 페이지 분리 확인
        # ptpNo=7 (112A) vs ptpNo=8 (112B) 실거래가 비교
        for ptp_name, ptp_no in TEST_PTPS:
            page = ctx.new_page()
            url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1&ptpNo={ptp_no}"
            page.goto(url, wait_until='domcontentloaded', timeout=25000)
            time.sleep(3)

            # 시세/실거래가 클릭
            for sel in ["button.complex_data_button"]:
                btns = page.locator(sel).all()
                for btn in btns:
                    if '실거래가' in (btn.inner_text() or ''):
                        btn.click()
                        time.sleep(2.5)
                        break

            # 더보기
            try:
                page.locator("button.btn_moretab").first.click()
                time.sleep(1)
            except: pass

            # 거래 테이블
            rows = page.locator('.detail_data_table tbody tr').all()
            print(f"\n[{ptp_name}, ptpNo={ptp_no}] 실거래가:")
            for row in rows[:5]:
                try:
                    cells = row.locator('th, td').all()
                    texts = [c.inner_text().strip() for c in cells]
                    print(f"  {texts}")
                except: pass

            # URL 내 ptpNo 파라미터가 제대로 반영되는지 확인
            # -> 다른 ptpNo면 다른 거래가 나와야 함
            page.close()

        print("\nEnter 누르면 종료...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
