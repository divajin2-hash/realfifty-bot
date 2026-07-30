import sys
import io
import json
from playwright.sync_api import sync_playwright

def get():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            extra_http_headers={"Referer": "https://new.land.naver.com/complexes/"}
        )
        page = context.new_page()
        page.goto(f"https://new.land.naver.com/complexes/3037", wait_until="commit", timeout=5000)
        
        # Then API
        url = f"https://new.land.naver.com/api/complexes/3037"
        response = context.request.get(url)
        data = response.json()
        if "result" in data and "complexPyeongDetailList" in str(data["result"]):
            ptps = data["result"].get("complexDetail", {}).get("complexPyeongDetailList", [])
            for pt in ptps: print(pt.get("pyeongNo"), pt.get("pyeongNm"), pt.get("exclusiveArea"))
        else:
            print("NO")
        browser.close()

get()
