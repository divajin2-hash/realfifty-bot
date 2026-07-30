from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://new.land.naver.com/complexes/3037?a=APT&b=A1", wait_until='networkidle')
    time.sleep(2)
    print(page.locator(".complex_title").inner_text())
    browser.close()
