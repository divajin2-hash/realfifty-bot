import sys
from playwright.sync_api import sync_playwright

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36')
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()
        page.goto('https://new.land.naver.com')
        page.wait_for_timeout(2000)
        
        print('Fetching via JS...')
        data = page.evaluate('''async () => {
            const res = await fetch("https://new.land.naver.com/api/complexes/111515/prices?ptpNo=1&tradeType=A1&year=3&priceChartBizes=KB");
            return await res.text();
        }''')
        print('Result:', data[:300])
        browser.close()

test()
