from curl_cffi import requests
import re
import json

res = requests.get('https://fin.land.naver.com/complexes/111515', impersonate='chrome110')
text = res.text

# dump the HTML to inspect
with open("dump.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Look for KB in dump.html")
matches = list(re.finditer(r'kb', text, re.IGNORECASE))
print("Found", len(matches), "occurrences of KB")
for m in matches[:5]:
    idx = m.start()
    snippet = text[max(0, idx-50):min(len(text), idx+100)].replace('\n','')
    print(">>>", snippet)
