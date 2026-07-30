import urllib.request
import json

def get_naver_ptps(nid):
    url = f"https://new.land.naver.com/api/complexes/{nid}?a=APT:ABYG:JGC&b=A1"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        html = urllib.request.urlopen(req).read().decode("utf-8")
        return json.loads(html)
    except Exception as e:
        print("Error:", e)
        return {}

data = get_naver_ptps("3037")
if "result" in data:
    ptps = data["result"].get("complexDetail", {}).get("complexPyeongDetailList", [])
    for p in ptps:
        ex = float(p.get("exclusiveArea", 0))
        rnd = round(ex)
        print(f"{p.get('pyeongNm')}: {ex} -> int({int(ex)}), round({rnd})")
