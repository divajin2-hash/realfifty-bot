import sys
import time
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        urls = []
        texts = []
        def intercept(res):
            if 'prices?ptpNo' in res.url:
                urls.append(res.status)
                try:
                    texts.append(res.json())
                except:
                    pass
                    
        page.on('response', intercept)
        
        print("Loading UI visibly to bypass 429...")
        page.goto('https://new.land.naver.com/complexes/111515?ms=37.497531,127.1064121,17&a=APT:ABYG:JGC&e=RETAIL')
        page.wait_for_timeout(5000)
        
        print('Intercepted statuses:', urls)
        if texts:
            if texts[0].get("success") is False:
                print("Failed:", texts[0])
            else:
                print("Success! Got price list!")
        else:
            print("No prices triggered.")
            
        browser.close()

if __name__ == "__main__":
    find_kb_api()
