from curl_cffi import requests
import re

res = requests.get('https://fin.land.naver.com/complexes/111515', impersonate='chrome110')
js_links = re.findall(r'src="(.*?\.js)"', res.text)
print('JS files:', js_links[:5])

for js in js_links:
    url = js if js.startswith('http') else 'https://fin.land.naver.com' + js
    r2 = requests.get(url, impersonate='chrome110')
    eps = re.findall(r'/front-api/v[0-9a-zA-Z_/]+', r2.text)
    if eps:
        print(f'Endpoints in {js}:', set(eps))
