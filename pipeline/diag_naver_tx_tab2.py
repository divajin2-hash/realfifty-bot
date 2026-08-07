"""
diag_naver_tx_tab2.py - 수정된 선택자로 타워팰리스 112A 탭 클릭 + 면적 추출 테스트
"""
import sys, io, time, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from playwright.sync_api import sync_playwright

NID = "634"
PTP_NO = "7"   # 112A

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1&ptpNo={PTP_NO}"
        print(f"접속: {url}")
        page.goto(url, wait_until='domcontentloaded', timeout=20000)
        time.sleep(3)  # JS 렌더링 대기

        # 탭 클릭 시도
        tab_clicked = False
        for sel in ["button.complex_data_button", "button.complex_link", "#detailContents3"]:
            try:
                btns = page.locator(sel).all()
                for btn in btns:
                    txt = btn.inner_text().strip()
                    if '실거래가' in txt:
                        print(f"클릭 시도: [{sel}] text={txt!r}")
                        btn.click()
                        time.sleep(2.5)
                        tab_clicked = True
                        break
                if tab_clicked:
                    break
            except Exception as e:
                print(f"실패 [{sel}]: {e}")

        if not tab_clicked:
            try:
                page.get_by_text('시세/실거래가', exact=True).first.click()
                time.sleep(2.5)
                tab_clicked = True
                print("텍스트 기반 클릭 성공")
            except Exception as e:
                print(f"텍스트 기반도 실패: {e}")

        print(f"탭 클릭: {'성공' if tab_clicked else '실패'}")

        if tab_clicked:
            # 실거래가 테이블 탐색
            print("\n=== 테이블 행 스캔 ===")
            for sel in ["table.table_real_price tbody tr", ".detail_data_table tbody tr", "table tbody tr"]:
                rows = page.locator(sel).all()
                if rows:
                    print(f"선택자 '{sel}' → {len(rows)}행")
                    for row in rows[:5]:
                        try:
                            cells = row.locator("th, td").all()
                            texts = [c.inner_text().strip() for c in cells]
                            print(f"  {texts}")
                        except:
                            pass
                    break

            # 페이지에서 ㎡ 패턴 추출
            print("\n=== 페이지 내 전용면적 추출 시도 ===")
            
            # 1. 페이지 텍스트 전체에서 소수점 면적 찾기
            page_text = page.evaluate("() => document.body.innerText")
            areas = re.findall(r'(\d{2,3}\.\d{1,2})\s*㎡', page_text)
            print(f"텍스트에서 발견된 면적들: {list(set(areas))[:10]}")
            
            # 2. HTML 소스에서 JSON 데이터 찾기
            html = page.content()
            json_areas = re.findall(r'"excluUseAr"\s*:\s*"?(\d+\.\d+)"?', html)
            print(f"HTML JSON excluUseAr: {list(set(json_areas))[:10]}")
            
            # 3. API 응답에서 직접 찾기
            area_patterns = re.findall(r'전용\s*(\d+\.\d+)', page_text)
            print(f"'전용 XX.XX' 패턴: {list(set(area_patterns))[:10]}")

        print("\n아무 키나 누르면 종료...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
