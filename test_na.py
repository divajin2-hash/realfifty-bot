from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    responses = []
    page.on("response", lambda r: responses.append((r.url, r)) if "complexPyeongDetailList" in r.url or "pyeongs" in r.url else None)
    
    # query APT ONLY
    page.goto("https://new.land.naver.com/complexes/3037?a=APT&b=A1", wait_until='networkidle')
    time.sleep(3)
    
    for url, r in responses:
        try:
            data = r.json()
            if "pyeongs" in data:
                ptps = data["pyeongs"]
            else:
                ptps = data.get('result', {}).get('complexDetail', {}).get('complexPyeongDetailList', [])
            if ptps:
                print("Found", len(ptps), "pyeongs in APT")
                for pt in ptps:
                    print(pt.get('pyeongNm') or pt.get('pyeongName'), pt.get('exclusiveArea'))
        except Exception as e:
            pass
    browser.close()
