import sys
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print("Loading old UI...")
        # ptpNo=1 directly loads the pyeong!
        page.goto('https://new.land.naver.com/complexes/111515?ptpNo=1&tradeType=A1', wait_until='domcontentloaded')
        page.wait_for_timeout(3000)
        
        body = page.locator('body').inner_text()
        import re
        if re.search(r'KB부동산 시세', body):
            print("Found KB Text on page load!")
            
        print("Clicking Sise Tab...")
        # The Sise tab in new.land.naver.com is usually a button with class containing '시세'
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('button, a, span'));
            for (let t of tabs) {
                if (t.innerText && t.innerText.trim() === '시세/실거래가') {
                    t.click();
                    break;
                }
            }
        }''')
        page.wait_for_timeout(3000)
        
        body = page.locator('body').inner_text()
        print(body[:1000])
        
        browser.close()

if __name__ == "__main__":
    find_kb_api()
