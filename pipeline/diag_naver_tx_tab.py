"""
diag_naver_tx_tab.py
타워팰리스 1차 112A 타입으로 네이버 부동산 실거래가 탭의 실제 HTML 구조를 파악
"""
import time
import re
from playwright.sync_api import sync_playwright

# 타워팰리스 1차: nid=634, 112A 타입=7번
NID = "634"
PTP_NO = "7"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        url = f"https://new.land.naver.com/complexes/{NID}?a=APT:ABYG:JGC&b=A1&ptpNo={PTP_NO}"
        print(f"URL: {url}")
        page.goto(url, wait_until='networkidle', timeout=20000)
        time.sleep(2)

        print("\n=== 탭 버튼 목록 ===")
        # 여러 탭 관련 선택자 시도
        tab_selectors = [
            "ul.tab_list li",
            ".tab_area button",
            ".complex_detail_tab li",
            "button[id*='detail']",
            "a[id*='detail']",
            ".detail_tab li",
            "li[id*='Contents']",
            "#detailContents1, #detailContents2, #detailContents3, #detailContents4",
        ]
        for sel in tab_selectors:
            els = page.locator(sel).all()
            if els:
                print(f"  선택자 '{sel}' → {len(els)}개:")
                for el in els[:5]:
                    try:
                        txt = el.inner_text().strip()[:50]
                        eid = el.get_attribute("id") or ""
                        print(f"    id={eid!r}  text={txt!r}")
                    except:
                        pass

        print("\n=== 실거래가 관련 텍스트 탐색 ===")
        # "실거래가" 텍스트가 있는 요소 찾기
        try:
            els = page.get_by_text("실거래가", exact=False).all()
            print(f"  '실거래가' 텍스트 요소 {len(els)}개:")
            for el in els[:5]:
                try:
                    tag = el.evaluate("el => el.tagName")
                    eid = el.get_attribute("id") or ""
                    cls = el.get_attribute("class") or ""
                    txt = el.inner_text().strip()[:60]
                    print(f"    tag={tag} id={eid!r} class={cls[:40]!r} text={txt!r}")
                except:
                    pass
        except Exception as e:
            print(f"  오류: {e}")

        print("\n=== 페이지 내 id 속성 목록 (detail 포함) ===")
        ids_with_detail = page.evaluate("""
            () => {
                const all = document.querySelectorAll('[id]');
                return Array.from(all)
                    .map(el => ({id: el.id, tag: el.tagName, text: el.innerText?.slice(0,30)}))
                    .filter(x => x.id.toLowerCase().includes('detail') || x.id.toLowerCase().includes('tab') || x.id.toLowerCase().includes('trade'));
            }
        """)
        for item in ids_with_detail[:20]:
            print(f"  id={item['id']!r} tag={item['tag']} text={item.get('text','')!r}")

        print("\n=== '시세/실거래가' 탭 클릭 시도 ===")
        # 여러 방식으로 클릭 시도
        clicked = False
        click_selectors = [
            ("텍스트 매칭", lambda: page.get_by_text("시세/실거래가").first.click()),
            ("텍스트 매칭2", lambda: page.get_by_text("실거래가").first.click()),
            ("#detailContents3", lambda: page.click("#detailContents3")),
            (".tab_list li:nth-child(3)", lambda: page.click(".tab_list li:nth-child(3)")),
        ]
        for name, click_fn in click_selectors:
            try:
                click_fn()
                time.sleep(1.5)
                print(f"  ✅ 클릭 성공: {name}")
                clicked = True
                break
            except Exception as e:
                print(f"  ❌ 클릭 실패 [{name}]: {e}")

        if clicked:
            time.sleep(1.5)
            print("\n=== 실거래가 테이블 탐색 ===")
            table_selectors = [
                "table.table_real_price tbody tr",
                ".detail_data_table tbody tr",
                ".real_price_table tbody tr",
                "table tbody tr",
            ]
            for sel in table_selectors:
                rows = page.locator(sel).all()
                if rows:
                    print(f"  선택자 '{sel}' → {len(rows)}행")
                    for row in rows[:3]:
                        try:
                            cells = row.locator("th, td").all()
                            texts = [c.inner_text().strip() for c in cells]
                            print(f"    {texts}")
                        except:
                            pass
                    break

            # 페이지 HTML 일부 저장
            html = page.content()
            # 실거래가 관련 부분만 추출
            m = re.search(r'(table_real_price.{0,3000})', html, re.DOTALL)
            if m:
                print(f"\n=== HTML 스니펫 (table_real_price) ===")
                print(m.group(1)[:1500])

        print("\n계속하려면 Enter...")
        input()
        browser.close()

if __name__ == '__main__':
    run()
