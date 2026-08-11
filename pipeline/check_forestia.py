"""
Check Naver tx for Forestia
"""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()

        nid = "118771" # 포레스티아
        url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1"
        page.goto(url, wait_until='domcontentloaded')
        time.sleep(3)

        # 시세/실거래가 탭
        page.evaluate("""() => {
            const btns = Array.from(document.querySelectorAll('button.complex_data_button, a.tab_item'));
            const btn = btns.find(b => b.innerText && b.innerText.includes('실거래가'));
            if(btn) btn.click();
        }""")
        time.sleep(2)
        try: page.locator("button.btn_moretab").first.click()
        except: pass
        time.sleep(1)

        types = ['108A㎡', '108B㎡', '112PA㎡', '113PC㎡', '114PD㎡']
        for t in types:
            try:
                tab = page.locator("a.detail_sorting_tab").filter(has_text=t).first
                tab.click(force=True)
                time.sleep(1)
                
                rows = page.locator('.detail_data_table tbody tr').all()
                if rows:
                    cells = rows[0].locator('th, td').all()
                    print(f"[{t}] 최신 실거래가: {cells[0].inner_text()} | {cells[1].inner_text()}")
                else:
                    print(f"[{t}] 거래 데이터 없음")
            except Exception as e:
                print(f"[{t}] 탭 매칭 실패: {e}")
                
        browser.close()

if __name__ == '__main__':
    run()
