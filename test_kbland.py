import requests
import json

def get_kb_price(keyword="아시아선수촌"):
    # Step 1: Search for the complex to get its KBLand ID (CortarNo or hscmNo)
    search_url = f"https://api.kbland.kr/api-gateway/search/v2/search/autoComplete?keyword={keyword}&pageNo=1&pageSize=10"
    res = requests.get(search_url, headers={'User-Agent': 'Mozilla/5.0'})
    print("Search Status:", res.status_code)
    
    if res.status_code == 200:
        data = res.json()
        print("Data:", data)

get_kb_price()
