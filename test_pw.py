import sys
from playwright.sync_api import sync_playwright

def test_pw():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        url = "https://new.land.naver.com/api/complexes/111515/prices?ptpNo=1&tradeType=A1&year=3&priceChartBizes=KB"
        page.goto(url)
        content = page.locator("body").inner_text()
        print("CONTENT:")
        print(content[:500])
        browser.close()

if __name__ == '__main__':
    test_pw()
