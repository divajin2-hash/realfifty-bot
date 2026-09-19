import sys
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        urls = []
        def intercept(res):
            if '/front-api/v' in res.url:
                urls.append(res.url)
                    
        page.on('response', intercept)
        
        print("Visiting fin.land.naver.com...")
        page.goto('https://fin.land.naver.com/complexes/111515?articleSortType=PRICE_ASC')
        page.wait_for_timeout(5000)
            
        print('Intercepted URLs:')
        for u in set(urls):
            print(u)
            
        browser.close()

if __name__ == "__main__":
    test()
