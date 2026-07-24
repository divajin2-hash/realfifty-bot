import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
            viewport={"width": 1920, "height": 1080}
        )
        
        page.goto("https://new.land.naver.com/complexes/111515?a=APT&b=A1")
        page.wait_for_timeout(5000)
        
        page.screenshot(path="naver_test.png")
        print("Screen saved to naver_test.png")
        
        browser.close()

test()
