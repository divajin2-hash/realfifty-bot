import os
import json
import requests
import xml.etree.ElementTree as ET
import datetime

def run():
    import urllib.parse
    
    # 팩트체크에 적합하도록 '가격', '거래량' 관련 키워드로 한정
    query = '아파트 (신고가 OR 하락 OR 폭락 OR 반등 OR 거래량 OR 거래절벽 OR 호가)'
    encoded_query = urllib.parse.quote(query)
    url = f'https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko'

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
