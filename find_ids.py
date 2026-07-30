import os
import urllib.parse
import re
from playwright.sync_api import sync_playwright

def find_ids():
    complexes = [
        ("헬리오시티", "송파구"),
        ("디에이치퍼스티어아이파크", "강남구"),
        ("잠실엘스", "송파구"),
        ("래미안원베일리", "서초구"),
        ("리센츠", "송파구"),
        ("은마", "강남구"),
        ("반포자이", "서초구"),
    ]
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        for name, region in complexes:
            query = urllib.parse.quote(f"{region} {name} 아파트 네이버 부동산")
            page.goto(f"https://search.naver.com/search.naver?query={query}")
            # get all links
            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href")
                if href and "new.land.naver.com/complexes/" in href:
                    match = re.search(r'complexes/(\d+)', href)
                    if match:
                        print(f"{name} -> {match.group(1)}")
                        break
        b.close()

find_ids()
