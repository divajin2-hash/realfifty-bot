import urllib.parse
import re
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    for keyword in ['대치 은마 네이버 부동산', '잠실 엘스 네이버 부동산', '마포래미안푸르지오 네이버 부동산', '반포자이 네이버 부동산']:
        q = urllib.parse.quote(keyword)
        page.goto('https://search.naver.com/search.naver?query=' + q)
        hrefs = page.evaluate("Array.from(document.querySelectorAll('a')).map(a => a.href).filter(h => h.includes('complexes/'))")
        for h in hrefs:
            if re.search(r'complexes/\d+', h):
                print(keyword, h)
                break
    b.close()
