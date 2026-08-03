import os, json, time, re
from playwright.sync_api import sync_playwright
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

mapping = json.load(open('pipeline/naver_complex_mapping.json'))
c_data = sb.table('complexes').select('id, complex_no').execute().data
py_stats = sb.table('pyeong_stats').select('id, complex_id, match_key_area, pyeong_name').execute().data

def ex_map(k): return int(round(float(k)))

to_update = []

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    page = context.new_page()
    
    for c in c_data:
        cid = c['id']
        cno = str(c['complex_no'])
        nids = mapping.get(cno, [])
        if isinstance(nids, str): nids = [nids]
        
        c_map = {}
        for nid in nids:
            found_api_url = None
            target_info = None

            def handle_res(response):
                nonlocal found_api_url, target_info
                if found_api_url: return
                if "complex" in response.url.lower() or "overview" in response.url.lower():
                    try:
                        data = response.json()
                        if "complexPyeongDetailList" in str(data) or "pyeongs" in str(data):
                            found_api_url = response.url
                            target_info = data
                    except: pass

            page.on("response", handle_res)
            try:
                page.goto(f"https://new.land.naver.com/complexes/{nid}", wait_until="networkidle", timeout=10000)
            except: pass
            
            page.wait_for_timeout(1000)
            page.remove_listener("response", handle_res)
            
            if target_info:
                ptps = []
                if "pyeongs" in target_info: ptps = target_info["pyeongs"]
                elif "result" in target_info and "complexDetail" in target_info["result"]:
                    ptps = target_info["result"]["complexDetail"].get("complexPyeongDetailList", [])
                elif "complexPyeongDetailList" in target_info:
                    ptps = target_info["complexPyeongDetailList"]
                    
                for p in ptps:
                    ex = float(p.get('exclusiveArea', 0))
                    nm = p.get('pyeongNm', p.get('pyeongName', ''))
                    m = re.match(r'^(\d+)', nm)
                    if m and ex > 0:
                        c_map[ex_map(ex)] = m.group(1)
        
        # compare with py_stats
        for ps in py_stats:
            if ps['complex_id'] == cid:
                mk = int(ps['match_key_area'])
                if mk in c_map:
                    if not ps['pyeong_name'] or ps['pyeong_name'] != c_map[mk]:
                        to_update.append({'id': ps['id'], 'pyeong_name': c_map[mk]})

print(f"{len(to_update)} areas to heal!")
for i in range(0, len(to_update), 100):
    sb.table('pyeong_stats').upsert(to_update[i:i+100]).execute()
print("DB Healed!")
