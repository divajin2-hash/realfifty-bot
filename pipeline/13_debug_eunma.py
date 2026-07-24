import sys
import io
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

def test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://new.land.naver.com/complexes/8928?a=APT&b=A1&prcSort=asc", wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        
        card = page.locator(".item_inner").first
        print("첫번째 카드 텍스트 원본:")
        print(card.inner_text())
        browser.close()

test()
