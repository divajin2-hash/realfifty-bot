import sys
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        urls = []
        def intercept(req):
            if req.resource_type in ['xhr', 'fetch'] and ('/front-api/' in req.url or '/api' in req.url or 'graphql' in req.url):
                urls.append(req.url)
        page.on('request', intercept)
        
        print("Loading UI...")
        page.goto('https://fin.land.naver.com/complexes/111515?articleSortType=PRICE_ASC')
        page.wait_for_timeout(3000)
        
        # Click the '시세' tab manually by evaluating a precise DOM JS
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('button, a, span'));
            for (let t of tabs) {
                if (t.innerText && t.innerText.trim() === '시세') {
                    t.click();
                    break;
                }
            }
        }''')
        page.wait_for_timeout(3000)
        
        print("Found API endpoints:")
        for u in set(urls):
            print(">>>", u)
            
            
        print("Now taking screenshot of the page to see if click worked...")
        page.screenshot(path="kb_debug.png")
        browser.close()

if __name__ == "__main__":
    find_kb_api()
