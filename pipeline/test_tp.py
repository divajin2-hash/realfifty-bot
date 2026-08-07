"""
test_tp.py
타워팰리스 1차(3038)의 실제 타입 탭 셀렉터 구조 확인
"""
import time, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = ctx.new_page()

        # 타워팰리스 1차 nid=3038
        url = "https://new.land.naver.com/complexes/3038?a=APT:ABYG:JGC&b=A1"
        print(f"접속: {url}")
        page.goto(url, wait_until='domcontentloaded', timeout=15000)
        time.sleep(3)
        
        # 탭 클릭
        clicked = page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button.complex_data_button, button.complex_link, a.tab_item'));
                const btn = btns.find(b => b.innerText && b.innerText.includes('실거래가'));
                if(btn){ btn.click(); return true; }
                return false;
            }
        """)
        print(f"시세/실거래가 탭 클릭: {clicked}")
        time.sleep(2)

        try:
            page.locator("button.btn_moretab").first.click()
            time.sleep(1)
        except: pass

        # 면적 탭들
        tabs = page.locator("a.detail_sorting_tab").all()
        texts = [t.inner_text().strip() for t in tabs]
        print(f"면적 탭 목록 ({len(texts)}개): {texts}")
        
        # 112가 들어간 탭의 거래 1개씩만
        for t in texts:
            if '112' in t:
                try:
                    tab_el = page.locator("a.detail_sorting_tab").filter(has_text=t).first
                    tab_el.click()
                    time.sleep(2)
                    rows = page.locator('.detail_data_table tbody tr').all()
                    if rows:
                        cells = rows[0].locator('th, td').all()
                        print(f"[{t}] 최신 거래: {cells[0].inner_text()} | {cells[1].inner_text()}")
                except Exception as e:
                    print(f"오류: {t} - {e}")
                    
        browser.close()

if __name__ == '__main__':
    run()
