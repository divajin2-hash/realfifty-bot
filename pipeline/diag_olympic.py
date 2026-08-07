"""
diag_olympic.py
올림픽선수기자촌 (nid=634) 시세/실거래가 탭에서
112A㎡ vs 112B㎡ 타입탭이 분리되어있는지, 각각 다른 거래가 나오는지 확인
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

# 올림픽선수기자촌: nid=142155
# pyeong_map에서 확인: 112A=ptp_no7, 112B=ptp_no8 (supply ~112㎡, exclusive 84.98)
NID = "142155"

def click_tab_and_get_tx(page, area_label):
    """시세/실거래가 탭 click 후 특정 면적 탭 클릭 -> 거래 목록 반환"""
    rows = page.locator('.detail_data_table tbody tr').all()
    txs = []
    for row in rows[:7]:
        try:
            cells = row.locator('th, td').all()
            if len(cells) < 2: continue
            dt = cells[0].inner_text().strip()
            pr = cells[1].inner_text().strip()
            if '.' in dt and pr:
                txs.append(f"{dt} | {pr}")
        except: pass
    return txs

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1"
        print(f"접속: {url}")
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # 1. 시세/실거래가 탭 클릭 (JS로 강제 클릭 - visibility 무관)
        clicked = page.evaluate("""
            () => {
                // 여러 선택자 시도
                const selectors = [
                    'button.complex_data_button',
                    'button.complex_link',
                    'a.tab_item',
                    'a[href*="trade"]'
                ];
                for (const sel of selectors) {
                    const btns = Array.from(document.querySelectorAll(sel));
                    const btn = btns.find(b => b.innerText && b.innerText.includes('실거래가'));
                    if (btn) {
                        btn.click();
                        return sel + ':' + btn.innerText.trim();
                    }
                }
                return null;
            }
        """)
        print(f"시세/실거래가 클릭: {clicked}")
        time.sleep(3)

        # 2. 더보기 버튼
        try:
            page.locator("button.btn_moretab").first.click()
            time.sleep(1)
            print("더보기 클릭")
        except: pass

        # 3. detail_sorting_tab 전체 목록
        tabs = page.locator("a.detail_sorting_tab").all()
        tab_texts = []
        for tab in tabs:
            try:
                txt = tab.inner_text().strip()
                if txt: tab_texts.append(txt)
            except: pass
        print(f"\n탭 목록 ({len(tab_texts)}개):")
        print(tab_texts)

        # 4. 112 관련 탭 찾기
        tabs_112 = [t for t in tab_texts if '112' in t]
        print(f"\n112 관련 탭: {tabs_112}")

        # 5. 각 112 탭 클릭 시 거래 비교
        results = {}
        for tab_text in tabs_112:
            try:
                tab_el = page.locator("a.detail_sorting_tab").filter(has_text=tab_text).first
                tab_el.scroll_into_view_if_needed(timeout=5000)
                tab_el.click(force=True)
                time.sleep(2)
                print(f"\n[{tab_text}] 클릭 후 거래:")
                txs = click_tab_and_get_tx(page, tab_text)
                results[tab_text] = txs
                for tx in txs[:5]:
                    print(f"  {tx}")
            except Exception as e:
                print(f"  [{tab_text}] 오류: {e}")
                results[tab_text] = []

        # 비교
        if len(results) >= 2:
            keys = list(results.keys())
            if results.get(keys[0]) == results.get(keys[1]):
                print(f"\n!! {keys[0]} vs {keys[1]}: 동일한 거래 -> 필터링 안됨")
            else:
                print(f"\n[{keys[0]}] vs [{keys[1]}]: 서로 다른 거래! -> 필터링 작동!")
                a_set = set(results.get(keys[0], []))
                b_set = set(results.get(keys[1], []))
                print(f"  {keys[0]} 전용: {a_set - b_set}")
                print(f"  {keys[1]} 전용: {b_set - a_set}")

        print("\nEnter 누르면 종료...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
