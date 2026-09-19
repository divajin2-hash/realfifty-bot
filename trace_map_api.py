import sys
from playwright.sync_api import sync_playwright

def find_kb_api():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        urls = []
        def handle_response(response):
            if "naver.com" in response.url and ("api" in response.url or "graphql" in response.url):
                try:
                    text = response.text()
                    if "58000" in text or "54000" in text or "KB부동산" in text or "상위" in text:
                        urls.append((response.url, text[:200]))
                except: pass
                
        page.on('response', handle_response)
        
        # Load the map view just like the screenshot
        url = "https://fin.land.naver.com/map?complexNumber=111515&tradeTypes=A1&pyeongTypeNo=1"
        print("Loading UI...")
        page.goto(url)
        page.wait_for_timeout(5000)
        
        print("Clicking Sise...")
        page.evaluate('''() => {
            const tabs = Array.from(document.querySelectorAll('span.text'));
            const siseTab = tabs.find(t => t.innerText && t.innerText.includes('시세'));
            if (siseTab) siseTab.click();
        }''')
        page.wait_for_timeout(4000)
        
        print("Found matching APIs with KB data:")
        for u in set([x[0] for x in urls]):
            print(u)
            
        browser.close()

if __name__ == "__main__":
    find_kb_api()
