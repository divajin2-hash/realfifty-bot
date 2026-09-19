from curl_cffi import requests
res = requests.get('https://fin.land.naver.com/complexes/111515', impersonate='chrome110')
import json
import re

html = res.text
matches = set(re.findall(r'"([a-zA-Z]*price[a-zA-Z]*)"', html, re.IGNORECASE))
print("Price-related keys in payload:")
print(matches)

# Let's extract Next.js built data 
# Specifically window.__NEXT_DATA__ doesn't exist, but maybe "initialData" or something
script_match = re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', html)
if script_match:
    print("Found NEXT_DATA!")
else:
    print("No NEXT_DATA found.")
