import re
from curl_cffi import requests as c_req

res = c_req.get('https://fin.land.naver.com/complexes/111515', impersonate='chrome110')
js_links = re.findall(r'src="(.*?\.js)"', res.text)
endpoints = set()

for js in js_links:
    url = js if js.startswith('http') else 'https://fin.land.naver.com' + js
    if js.startswith('/'):
        url = 'https://fin.land.naver.com' + js
    elif not js.startswith('http'):
        url = 'https://property.pstatic.net/property-web' + js # fallback based on source

    try:
        j_res = c_req.get(url, impersonate='chrome110')
        eps = re.findall(r'/front-api/[a-zA-Z0-9_/-]+', j_res.text)
        for ep in eps:
            endpoints.add(ep)
    except: pass
    
for ep in sorted(endpoints):
    if 'price' in ep.lower() or 'chart' in ep.lower() or 'sise' in ep.lower() or 'kb' in ep.lower():
        print("MATCH:", ep)
