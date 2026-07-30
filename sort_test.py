from playwright.sync_api import sync_playwright
import time

def parse_korean_price(price_str):
    import re
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        digits_only = re.sub(r'[^0-9]', '', parts[1])
        man = int(digits_only) * 10000 if digits_only else 0
        return eok + man
    digits_only = re.sub(r'[^0-9]', '', clean_str)
    return int(digits_only) * 10000 if digits_only else 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
    context = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36')
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    page = context.new_page()
    page.goto('https://new.land.naver.com/complexes/111515?ms=37.497554,127.10649,17&a=APT&b=A1&ptpNo=1', wait_until='networkidle', timeout=15000)
    time.sleep(2)
    
    print("Default top 3 prices:")
    cards = page.locator(".item_inner").all()[:3]
    for c in cards: print(c.locator('.price').first.inner_text().strip())
    
    print("\nClicking TAA.price (가격순)...")
    price_sort_btn = page.locator("a[data-nclk='TAA.price']")
    price_sort_btn.click()
    time.sleep(2)
    
    print("Class of price sort button:", price_sort_btn.get_attribute("class"))
    
    print("\nAfter 1st click, top 3 prices:")
    cards = page.locator(".item_inner").all()[:3]
    for c in cards: print(c.locator('.price').first.inner_text().strip())
    
    print("\nClicking TAA.price (가격순) again...")
    price_sort_btn.click()
    time.sleep(2)
    print("Class of price sort button:", price_sort_btn.get_attribute("class"))
    
    print("\nAfter 2nd click, top 3 prices:")
    cards = page.locator(".item_inner").all()[:3]
    for c in cards: print(c.locator('.price').first.inner_text().strip())

    browser.close()
