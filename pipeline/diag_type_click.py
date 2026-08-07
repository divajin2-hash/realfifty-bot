"""
diag_type_click.py
====================================================================
핵심 검증: 네이버 실거래가 탭 내 타입 버튼 클릭으로 타입별 거래 필터링 확인

테스트: 타워팰리스 1차
  - nid=634
  - 112A (ptp_no=7, 전용 84.98) 
  - 112B (ptp_no=8, 전용 84.98)
  -> 두 타입의 거래 목록이 달라야 함
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from playwright.sync_api import sync_playwright

NID = "634"  # 타워팰리스 1차

# 112A=7, 112B=8 (pyeong_map에서 확인)
TEST_TYPES = [
    {"ptp_name": "112A", "ptp_no": "7"},
    {"ptp_name": "112B", "ptp_no": "8"},
]

def get_tx_for_type(context, nid, ptp_name, ptp_no):
    page = context.new_page()
    try:
        # 단지 페이지 로드 (ptpNo 포함 - 타입 기본 선택용)
        url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1&ptpNo={ptp_no}"
        print(f"\n  [{ptp_name}] 접속 중...")
        page.goto(url, wait_until='domcontentloaded', timeout=25000)
        time.sleep(3)

        # 1단계: "시세/실거래가" 탭 클릭
        clicked_tab = False
        for sel in ["button.complex_data_button", "button.complex_link"]:
            try:
                btns = page.locator(sel).all()
                for btn in btns:
                    if '실거래가' in btn.inner_text():
                        btn.click()
                        time.sleep(2.5)
                        clicked_tab = True
                        break
                if clicked_tab:
                    break
            except:
                pass
        
        if not clicked_tab:
            print(f"  [{ptp_name}] 탭 클릭 실패")
            return []

        print(f"  [{ptp_name}] 실거래가 탭 클릭 성공. 타입 버튼 탐색...")

        # 2단계: 탭 안에서 타입 버튼들 확인
        # 타입명 예: "112A㎡", "112B㎡"
        # 여러 선택자 시도
        type_btn_clicked = False
        type_btn_selectors = [
            "button.ptpTab",
            ".ptp_tab button",
            "button[class*='ptp']",
            ".complex_tab_type button",
            ".type_tab button",
            "ul.tab_list_type li",
            "button[class*='type']",
        ]
        
        print(f"  [{ptp_name}] 타입 버튼 선택자 탐색:")
        for sel in type_btn_selectors:
            try:
                btns = page.locator(sel).all()
                if btns:
                    print(f"    선택자 '{sel}' -> {len(btns)}개")
                    for btn in btns[:5]:
                        txt = btn.inner_text().strip()
                        print(f"      text={txt!r}")
            except:
                pass

        # 실제로 페이지에서 ptp_name과 일치하는 버튼 찾아 클릭
        # ptp_name="112A" -> "112A㎡" 버튼 찾기
        for text_pattern in [f"{ptp_name}㎡", ptp_name, f"{ptp_name} "]:
            try:
                el = page.get_by_text(text_pattern, exact=True).first
                if el:
                    el.click()
                    time.sleep(1.5)
                    type_btn_clicked = True
                    print(f"  [{ptp_name}] 타입 버튼 클릭 성공: '{text_pattern}'")
                    break
            except:
                pass
        
        if not type_btn_clicked:
            print(f"  [{ptp_name}] 타입 버튼 클릭 실패 -> 탭 클릭 후 기본 상태 그대로")

        # 3단계: 실거래가 테이블 읽기
        time.sleep(1.5)
        rows = page.locator('.detail_data_table tbody tr').all()
        results = []
        for row in rows[:7]:
            try:
                cells = row.locator('th, td').all()
                if len(cells) >= 2:
                    dt = cells[0].inner_text().strip()
                    pr = cells[1].inner_text().strip()
                    if '.' in dt and pr:
                        results.append(f"{dt} | {pr}")
            except:
                pass

        print(f"  [{ptp_name}] 거래 {len(results)}건:")
        for r in results[:5]:
            print(f"    {r}")

        # 4단계: 타입 선택 탭 영역 HTML 스니펫 (디버깅용)
        html = page.content()
        # 타입 탭 영역 패턴 찾기
        patterns = [
            r'ptpTab[^}]{0,500}',
            r'ptp_tab[^}]{0,500}',
            r'112A[^<]{0,200}',
        ]
        for pat in patterns:
            m = re.search(pat, html)
            if m:
                print(f"\n  HTML 스니펫({pat[:10]}...):\n  {m.group()[:300]}")
                break

        return results
    finally:
        page.close()

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        print("=== 타워팰리스 1차 타입별 실거래가 비교 ===")
        
        results = {}
        for t in TEST_TYPES:
            results[t['ptp_name']] = get_tx_for_type(context, NID, t['ptp_name'], t['ptp_no'])
            time.sleep(1)

        print("\n=== 비교 결과 ===")
        for name, txs in results.items():
            print(f"\n[{name}]")
            for tx in txs[:5]:
                print(f"  {tx}")

        a_set = set(results.get('112A', []))
        b_set = set(results.get('112B', []))
        if a_set == b_set:
            print("\n!! 두 타입의 거래가 동일 - 타입 필터링이 안 되고 있음")
        else:
            print(f"\n타입별로 다른 거래 - 필터링 작동!")
            print(f"  112A 전용: {a_set - b_set}")
            print(f"  112B 전용: {b_set - a_set}")

        input("\n아무 키나 누르면 종료...")
        context.close()
        browser.close()

if __name__ == '__main__':
    run()
