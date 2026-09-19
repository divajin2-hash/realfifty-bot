import sys
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        urls = []
        def intercept(res):
            if '/front-api/' in res.url:
                urls.append(res.url)
        page.on('response', intercept)
        
        print("Loading UI...")
        page.goto('https://fin.land.naver.com/complexes/111515')
        page.wait_for_timeout(3000)
        
        print("Evaluating click via JS to bypass locator errors...")
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('span.text'));
            const siseTab = tabs.find(t => t.innerText.includes('시세'));
            if (siseTab) siseTab.click();
        }''')
        page.wait_for_timeout(3000)
        
        print("Found API endpoints:")
        for u in set(urls):
            print(">>>", u)
        
        browser.close()

if __name__ == "__main__":
    find_kb_api()
