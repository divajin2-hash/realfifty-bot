import requests
url = "https://api.kbland.kr/land-complex/complex/hscm/111515"
res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print("Status:", res.status_code)
if res.status_code == 200:
    print(res.text[:300])
