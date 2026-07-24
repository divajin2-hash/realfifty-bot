import sys
import io
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/1920 height/1080")
        page = context.new_page()
        page.goto("https://new.land.naver.com/api/complexes/111515")
        print("API:", page.locator("body").inner_text()[:300])
        
        page.goto("https://new.land.naver.com/complexes/111515")
        page.wait_for_selector(".complex_title")
        print("UI Title:", page.locator(".complex_title").inner_text())
        browser.close()
        
test()
