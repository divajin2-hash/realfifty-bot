import os
import json
import datetime
from playwright.sync_api import sync_playwright

def run():
    print("\nStarting Naver Real Estate News Crawler...")
    url = 'https://land.naver.com/news/headline.naver'

    articles = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')

        # Fetch top headlines from Naver Real Estate
        blocks = page.locator("ul.headline_list > li").all()
        for block in blocks:
            try:
                a_tag = block.locator("dt:not(.photo) > a")
                if a_tag.count() == 0:
                    a_tag = block.locator("dt.photo > a")
                
                title = a_tag.inner_text().strip()
                link = "https://land.naver.com" + a_tag.first.get_attribute("href")
                
                # Content snippet
                summary = ""
                dd_tag = block.locator("dd")
                if dd_tag.count() > 0:
                    summary = dd_tag.first.inner_text().split("\n")[0].strip()
                
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary
                })
            except Exception as e:
                print("Error parsing article bloc:", e)
        browser.close()

    if not articles:
        print("No articles found!")
        return

    print(f"Parsed {len(articles)} headline articles. Saving to JSON...")
    
    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'latest_news.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    print(f"✅ News articles properly saved at {out_path}!")

if __name__ == '__main__':
    run()
