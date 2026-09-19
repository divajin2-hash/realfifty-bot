import json
from playwright.sync_api import sync_playwright

def trace_network():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        requests_made = []
        def handle_request(route, request):
            if request.method == "POST":
                requests_made.append({
                    "url": request.url,
                    "post_data": request.post_data
                })
            route.continue_()
            
        page.route("**/*", handle_request)
        
        print("Loading...")
        page.goto("https://fin.land.naver.com/complexes/111515?articleSortType=PRICE_ASC", wait_until="networkidle")
        page.wait_for_timeout(3000)
        
        print("Clicking Sise...")
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
        
        print(f"Total POST requests intercepted: {len(requests_made)}")
        for req in requests_made:
            if req['post_data']:
                if 'price' in req['post_data'].lower() or 'chart' in req['post_data'].lower():
                    print("Found relevant POST:", req['url'])
                    print("Data:", req['post_data'][:200])
                    
        browser.close()

if __name__ == "__main__":
    trace_network()
