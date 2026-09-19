import os
import sys
import time
import json
from playwright.sync_api import sync_playwright

def crawl_kb_sise_ui():
    print("==================================================")
    print(" [RealFifty V3] KB Market Price UI Scraper")
    print("==================================================")
    
    # 50 Complexes Example List (simplified for demo)
    target_complexes = [
        {"name": "아시아선수촌", "nid": "144", "ptp": "1"} # 50평형 등 
    ]
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        for c in target_complexes:
            print(f"\n▶ [{c['name']}] KB 시세 (fin.land) 추출 중...")
            try:
                # Type A1 is 매매
                url = f"https://fin.land.naver.com/complexes/{c['nid']}?articleSortType=PRICE_ASC"
                page.goto(url)
                page.wait_for_timeout(3000)
                
                # 시세 탭 클릭 
                page.evaluate('''() => {
                    const tabs = Array.from(document.querySelectorAll('span.text'));
                    const siseTab = tabs.find(t => t.innerText.includes('시세'));
                    if (siseTab) siseTab.click();
                }''')
                page.wait_for_timeout(3000)
                
                # KB부동산 시세 텍스트 추출 (DOM 긁기)
                body_text = page.locator("body").inner_text()
                
                # Parse bounds
                print("Extracted Body Text Snippet:")
                print(body_text[:1000]) # debug
                
            except Exception as e:
                print("Error:", e)
                
        browser.close()

if __name__ == "__main__":
    crawl_kb_sise_ui()
