import sys
import time
import re
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print("Loading UI...")
        page.goto('https://fin.land.naver.com/complexes/111515?articleSortType=PRICE_ASC')
        page.wait_for_timeout(3000)
        
        print("Clicking Sise Tab...")
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('button, a, span'));
            for (let t of tabs) {
                if (t.innerText && t.innerText.trim() === '시세') {
                    t.click();
                    break;
                }
            }
        }''')
        page.wait_for_timeout(3000)
        
        # Scrape all inner texts 
        body_text = page.locator("body").inner_text()
        
        # Look for the exact format: "상위 58억 5,000" or similar as shown in screenshot
        # The screenshot shows: "상위 58억 5,000", "하위 54억 5,000"
        m_top = re.search(r'상위\s+([0-9]+억\s*[0-9,]*)', body_text)
        m_bot = re.search(r'하위\s+([0-9]+억\s*[0-9,]*)', body_text)
        m_avg = re.search(r'평균\s+([0-9]+억\s*[0-9,]*)', body_text)
        m_kb = re.search(r'KB부동산 시세', body_text)
        
        print("KB Text Found:", bool(m_kb))
        if m_top: print("Top Price:", m_top.group(1))
        if m_bot: print("Bot Price:", m_bot.group(1))
        
        browser.close()

if __name__ == "__main__":
    find_kb_api()
