import requests
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://new.land.naver.com/complexes/",
        "Accept": "application/json, text/plain, */*"
    }
    res = requests.get("https://new.land.naver.com/api/complexes/111515", headers=headers)
    print("STATUS:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("NAME:", data.get('complexName'))
        print("DATA:", len(data.get('complexPyeongDetailList', [])))
    else:
        print(res.text[:500])

test()
