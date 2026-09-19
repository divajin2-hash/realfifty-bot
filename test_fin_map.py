import sys
import re
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        url = "https://fin.land.naver.com/map?complexNumber=111515&tradeTypes=A1&pyeongTypeNo=1"
        print("Loading Map View:", url)
        # We need to wait for the page to load, but MAP is heavy
        page.goto(url, wait_until='networkidle')
        page.wait_for_timeout(3000)
        
        # Click "시세" tab
        print("Clicking SISE tab...")
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('button, a, span'));
            for (let t of tabs) {
                if (t.innerText && t.innerText.trim() === '시세') {
                    t.click();
                    break;
                }
            }
        }''')
        page.wait_for_timeout(2000)
        
        body = page.locator('body').inner_text()
        m_top = re.search(r'상위\s+([0-9]+억\s*[0-9,]*)', body)
        m_bot = re.search(r'하위\s+([0-9]+억\s*[0-9,]*)', body)
        
        if m_top: print("Top:", m_top.group(1))
        if m_bot: print("Bot:", m_bot.group(1))
        
        # Also print first 1000 chars of panel
        panel = page.locator('div[class*="panel"]').first
        if panel:
            print("Panel text:", panel.inner_text()[:500])
            
        browser.close()

if __name__ == "__main__":
    find_kb_api()
