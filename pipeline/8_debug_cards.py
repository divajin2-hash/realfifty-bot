import sys
import re
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def debug_cards(complex_no, name):
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&prcSort=asc"
    print(f"\n======================================")
    print(f"디버그: {name}")
    print(f"======================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        try:
            page.wait_for_selector(".item_inner", timeout=10000)
            cards = page.locator(".item_inner").all()[:5]
            
            for idx, card in enumerate(cards):
                text = card.inner_text().replace('\n', ' | ')
                try:
                    price = card.locator(".price").first.inner_text()
                except:
                    price = "No Price"
                print(f"[{idx+1}] 가격: {price}")
                print(f"    Raw텍스트: {text[:120]}...\n")
        except Exception as e:
            print("에러:", e)
        finally:
            browser.close()

if __name__ == "__main__":
    debug_cards("10586", "마포 래미안푸르지오")
    debug_cards("1424", "서초 반포자이")
