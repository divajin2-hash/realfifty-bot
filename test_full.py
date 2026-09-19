import sys
import re
from playwright.sync_api import sync_playwright

def extract_kb_price():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        # We use the mobile/desktop URL directly to the complex dashboard
        url = "https://fin.land.naver.com/complexes/111515?articleSortType=PRICE_ASC"
        print("Visiting Fin Land Naver...")
        page.goto(url, wait_until="networkidle")
        
        # In fin.land, the Sise is located in a tab or scroll area.
        # Let's extract ALL text
        text = page.locator("body").inner_text()
        print("Text Length:", len(text))
        
        with open("body_fin.txt", "w", encoding="utf-8") as f:
            f.write(text)
            
        print("Done.")
        browser.close()

if __name__ == "__main__":
    extract_kb_price()
