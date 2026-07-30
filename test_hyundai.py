import requests

nid = '3037'
url = f'https://new.land.naver.com/api/complexes/{nid}'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
try:
    r = requests.get(url, headers=headers)
    data = r.json()
    ptps = data.get('result', {}).get('complexDetail', {}).get('complexPyeongDetailList', [])
    if not ptps:
        print("Empty ptps, checking alternative API.")
    for p in ptps:
        print(f"ptpNo: {p.get('ptpNo')}, ptpName: {p.get('pyeongNm')}, exArea: {p.get('exclusiveArea')}, supplyArea: {p.get('supplyArea')}")
except Exception as e:
    print("Error:", e)
