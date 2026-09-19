import os
import json
import time
import re
from datetime import datetime
from playwright.sync_api import sync_playwright

def run_kb_scraper():
    print("==================================================")
    print(" [RealFifty V3] KB Market Price UI Scraper")
    print("==================================================")
    
    # 테스트용 임시 단지 리스트 (실제 병합 시 complexes_db 사용)
    target_complexes = [
        {"name": "아시아선수촌", "nid": "144", "ptp": "1"}  
        # 나중에 FULL_TARGET_MAPPING 이나 DB 에서 순회
    ]
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    results = []
    
    with sync_playwright() as p:
        # headless=False 로 방화벽(캡챠) 완전 회피
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        for c in target_complexes:
            print(f"\n▶ [{c['name']}] KB 시세 (fin.land) 추출 중...")
            
            # 신형 서버(fin.land)의 단지 상세페이지 직접 타격
            url = f"https://fin.land.naver.com/complexes/{c['nid']}?articleSortType=PRICE_ASC"
            print(f"URL 접속: {url}")
            page.goto(url)
            page.wait_for_timeout(3000)
            
            # [시세] 탭 누르기 (DOM 텍스트 기반)
            print("[시세] 탭 클릭 시도...")
            page.evaluate('''() => {
                const tabs = Array.from(document.querySelectorAll('button, a, span'));
                const siseTab = tabs.find(t => t.innerText && t.innerText.trim() === '시세');
                if (siseTab) siseTab.click();
            }''')
            page.wait_for_timeout(3000)
            
            # 본문 텍스트 전부 긁기
            body_text = page.locator("body").inner_text()
            
            # 정규식 패턴 매칭 (스크린샷 기준: "상위 58억 5,000", "하위 54억 5,000")
            m_top = re.search(r'상위\s+([0-9]+억\s*[0-9,]*)', body_text)
            m_bot = re.search(r'하위\s+([0-9]+억\s*[0-9,]*)', body_text)
            m_avg = re.search(r'평균\s+([0-9]+억\s*[0-9,]*)', body_text)
            
            kb_data = {
                "complex_name": c['name'],
                "nid": c['nid'],
                "kb_top_price": m_top.group(1) if m_top else None,
                "kb_avg_price": m_avg.group(1) if m_avg else None,
                "kb_bot_price": m_bot.group(1) if m_bot else None,
                "crawled_date": today_str
            }
            
            print(f"  └ 결과: 상위={kb_data['kb_top_price']}, 하위={kb_data['kb_bot_price']}")
            results.append(kb_data)
            
        browser.close()
        
    # 결과 저장
    out_path = f"raw_kb_prices_{today_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 임시 테스트 추출 완료! 파일 저장: {out_path}")

if __name__ == "__main__":
    run_kb_scraper()
