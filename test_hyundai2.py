from playwright.sync_api import sync_playwright
import time
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    responses = []
    def handle_response(response):
        if "pyeongs" in response.url or "complexPyeongDetailList" in response.url or "complex" in response.url:
            try:
                responses.append((response.url, response.json()))
            except:
                pass
    
    page.on("response", handle_response)
    page.goto("https://new.land.naver.com/complexes/3037?a=APT&b=A1", wait_until='networkidle')
    time.sleep(2)
    
    for url, data in responses:
        data_str = str(data)
        if 'complexPyeongDetailList' in data_str:
            print("FOUND IN:", url)
            ptps = data.get('result', {}).get('complexDetail', {}).get('complexPyeongDetailList', [])
            for p in ptps:
                print(f"ptpName: {p.get('pyeongName') or p.get('pyeongNm')}, exArea: {p.get('exclusiveArea')}")
        elif 'pyeongs' in data_str:
            print("FOUND IN:", url)
            ptps = data.get('pyeongs', [])
            for p in ptps:
                print(f"ptpName: {p.get('pyeongName') or p.get('pyeongNm')}, exArea: {p.get('exclusiveArea')}")
                
    browser.close()
