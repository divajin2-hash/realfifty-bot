"""
diag_type_click2.py
타워팰리스 1차: 시세/실거래가 탭 클릭 후 페이지 HTML 덤프해서
타입 버튼(112A, 112B 등) 선택자를 수동으로 확인
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from playwright.sync_api import sync_playwright

NID = "634"
PTP_NO = "7"  # 112A

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1&ptpNo={PTP_NO}"
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # 시세/실거래가 탭 클릭
        for sel in ["button.complex_data_button", "button.complex_link"]:
            try:
                btns = page.locator(sel).all()
                for btn in btns:
                    if '실거래가' in (btn.inner_text() or ''):
                        btn.click()
                        time.sleep(2.5)
                        print(f"탭 클릭 성공: {sel}")
                        break
            except:
                pass

        time.sleep(1)

        # 타입 버튼이 있을 법한 모든 버튼 출력
        print("\n=== 현재 페이지 모든 BUTTON 요소 ===")
        all_btns = page.evaluate("""
            () => Array.from(document.querySelectorAll('button, a[role=tab], li[role=tab]'))
                .filter(el => el.innerText && el.innerText.trim().length > 0 && el.innerText.trim().length < 30)
                .map(el => ({
                    tag: el.tagName,
                    cls: el.className || '',
                    txt: el.innerText.trim().replace(/\\n/g, ' '),
                    id: el.id || ''
                }))
        """)
        seen = set()
        for b in all_btns:
            key = f"{b['cls'][:40]}|{b['txt']}"
            if key not in seen:
                seen.add(key)
                print(f"  [{b['tag']}] cls={b['cls'][:50]!r} txt={b['txt']!r}")

        # "112" 포함 요소 찾기
        print("\n=== '112' 텍스트 포함 요소 ===")
        els_112 = page.evaluate("""
            () => Array.from(document.querySelectorAll('*'))
                .filter(el => el.childElementCount === 0 && el.innerText && el.innerText.includes('112'))
                .map(el => ({
                    tag: el.tagName,
                    cls: el.className || '',
                    txt: el.innerText.trim().slice(0, 50),
                    parent_cls: el.parentElement ? el.parentElement.className : ''
                }))
        """)
        for e in els_112[:20]:
            print(f"  [{e['tag']}] cls={e['cls'][:40]!r} txt={e['txt']!r} parent={e['parent_cls'][:40]!r}")

        # HTML 덤프 (타입 관련 부분)
        html = page.content()
        # 112A 주변 HTML
        idx = html.find('112A')
        if idx >= 0:
            snippet = html[max(0, idx-200):idx+400]
            print(f"\n=== HTML 주변 (112A 위치) ===")
            print(snippet[:600])

        print("\n아무 키나 누르면 종료...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
