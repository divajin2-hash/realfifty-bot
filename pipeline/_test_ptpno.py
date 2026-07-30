import sys
import io
import time
import re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
    ctx = b.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36')
    ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    page = ctx.new_page()

    # 1. ptpNo API 테스트
    print("1️⃣ ptpNo API 테스트 (헬리오시티)...")
    r = page.goto('https://new.land.naver.com/api/complexes/111515', wait_until='domcontentloaded', timeout=10000)
    data = r.json()
    print('  응답코드:', r.status)
    pyeongs = data.get('complexPyeongDetailList', [])
    print('  평형 수:', len(pyeongs))
    for py in pyeongs[:5]:
        print(f"  ptpNo={py.get('ptpNo')}, name={py.get('pyeongNm')}, exclusive={py.get('exclusiveArea')}")

    if pyeongs:
        ptp = str(pyeongs[0].get('ptpNo'))
        area = pyeongs[0].get('exclusiveArea')
        print(f"\n2️⃣ ptpNo={ptp} ({area}m2) 매물 최저가 조회...")
        url = f'https://new.land.naver.com/complexes/111515?a=APT&b=A1&ptpNo={ptp}&prcSort=asc'
        page.goto(url, wait_until='domcontentloaded', timeout=15000)
        page.wait_for_selector('.item_inner', timeout=10000)
        card = page.locator('.item_inner').first
        price = card.locator('.price').first.inner_text().strip()
        text = card.inner_text()[:60]
        print(f"  1순위 매물: {price}")
        print(f"  원문: {text}")

    b.close()
