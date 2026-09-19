import sys
from playwright.sync_api import sync_playwright

def crawl_kb_sise():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        
        # 1. Access main page to get bypass cookies
        print("Bypassing Naver Security...")
        page.goto('https://new.land.naver.com')
        page.wait_for_timeout(2000)
        
        # 2. Hit the KB API 
        api_url = "https://new.land.naver.com/api/complexes/111515/prices?ptpNo=1&tradeType=A1&year=3&priceChartBizes=KB"
        page.goto(api_url)
        content = page.locator("body").inner_text()
        
        if "TOO_MANY_REQUESTS" in content:
            print("Still blocked by 429.", content[:100])
        elif "priceChartList" in content:
            print("Successfully extracted KB Prices!!!")
            print(content[:300])
        else:
            print("Unknown response:", content[:200])
            
        browser.close()

if __name__ == "__main__":
    crawl_kb_sise()
