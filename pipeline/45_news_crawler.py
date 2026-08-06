import os
import json
import requests
import xml.etree.ElementTree as ET
import datetime

def run():
    print("\nStarting Google News RSS Crawler for Real Estate...")
    # Search for '부동산 아파트' (Real estate apartment) on Google News KR
    url = 'https://news.google.com/rss/search?q=%EB%B6%80%EB%8F%99%EC%82%B0+%EC%95%84%ED%8C%8C%ED%8A%B8&hl=ko&gl=KR&ceid=KR:ko'

    try:
        res = requests.get(url, timeout=10)
        root = ET.fromstring(res.text)
    except Exception as e:
        print("Failed to fetch or parse RSS:", e)
        return

    articles = []
    for item in root.findall('.//item')[:20]: # top 20 news
        title = item.findtext('title', '').strip()
        # Remove the source name at the end (e.g. " - 한국경제")
        if " - " in title:
            title = " - ".join(title.split(" - ")[:-1])
            
        link = item.findtext('link', '').strip()
        pub_date = item.findtext('pubDate', '').strip()
        source = item.findtext('source', '').strip()
        
        articles.append({
            "title": title,
            "link": link,
            "source": source,
            "pub_date": pub_date
        })

    if not articles:
        print("No articles found!")
        return

    print(f"Parsed {len(articles)} headline articles. Saving to JSON...")
    
    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'latest_news.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
        
    print(f"News articles properly saved at {out_path}!")

if __name__ == '__main__':
    run()
