"""
diag_tx_panel.py
시세/실거래가 패널 안에서 112A/112B 타입 탭 요소를 정확히 찾기
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

NID = "634"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1"
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # 시세/실거래가 탭 클릭
        for sel in ["button.complex_data_button"]:
            btns = page.locator(sel).all()
            for btn in btns:
                if '실거래가' in (btn.inner_text() or ''):
                    btn.click()
                    print(f"탭 클릭: {sel}")
                    time.sleep(3)
                    break

        # 더보기 버튼
        try:
            mb = page.locator("button.btn_moretab").first
            mb.click()
            time.sleep(1)
            print("더보기 클릭")
        except: pass

        # 핵심: 모든 a, button 요소 중 '112' 포함
        print("\n=== '112' 포함 클릭 가능 요소 ===")
        els = page.evaluate("""
            () => Array.from(document.querySelectorAll('a, button, li'))
                .filter(el => {
                    const t = el.innerText || '';
                    return t.includes('112') && t.length < 20;
                })
                .map(el => ({
                    tag: el.tagName,
                    cls: el.className || '',
                    txt: (el.innerText||'').trim().slice(0,30),
                    id: el.id || '',
                    href: el.href || ''
                }))
        """)
        for e in els:
            print(f"  [{e['tag']}] cls={e['cls']!r} id={e['id']!r} txt={e['txt']!r}")

        # ptp 관련 URL/href 탐색
        print("\n=== ptp 포함 href/onclick ===")
        ptp_els = page.evaluate("""
            () => Array.from(document.querySelectorAll('[href*="ptp"], [onclick*="ptp"], [data-ptp]'))
                .map(el => ({
                    tag: el.tagName,
                    cls: el.className || '',
                    txt: (el.innerText||'').trim().slice(0,30),
                    href: (el.href||'').slice(0,80),
                }))
        """)
        for e in ptp_els[:10]:
            print(f"  [{e['tag']}] cls={e['cls']!r} txt={e['txt']!r} href={e['href']!r}")

        # 시세/실거래가 패널의 HTML만 추출
        print("\n=== 실거래가 패널 내부 HTML (112 주변) ===")
        html = page.content()
        for pattern in ['112A', 'ptpTab', 'trade_type', 'complex_chart_type']:
            idx = html.find(pattern)
            if idx > 0:
                print(f"\n  [{pattern}] 위치 {idx}:")
                print(html[max(0,idx-150):idx+250])

        print("\n Enter 누르면 종료...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
