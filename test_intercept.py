import sys
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        results = []
        texts = []
        def intercept(res):
            if 'prices?ptpNo' in res.url:
                results.append(res.status)
                try: 
                    texts.append(res.json())
                except:
                    pass
                    
        page.on('response', intercept)
        
        print("Visiting Naver UI...")
        page.goto('https://new.land.naver.com/complexes/111515?ms=37.497531,127.1064121,17&a=APT:ABYG:JGC&e=RETAIL')
        page.wait_for_timeout(3000)
        
        try:
            # Click Sise Tab
            print("Clicking SISE tab...")
            page.locator("span.text", has_text="시세/실거래가").click(timeout=5000)
            page.wait_for_timeout(3000)
        except Exception as e:
            print('Click failed:', e)
            
        print('Intercepted statuses:', results)
        if texts:
            print("Intercepted JSON keys:", list(texts[0].keys()))
            if "success" in texts[0] and not texts[0]["success"]:
                print("API Failed message:", texts[0].get("message"))
            
        browser.close()

if __name__ == "__main__":
    test()
