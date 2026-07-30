import sys, os, time, json
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('pipeline/.env')
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

rtms_data = supabase.table("rtms_transactions").select("complex_id, match_key_area").execute().data
rtms_map = {}
for r in rtms_data:
    cid = r["complex_id"]
    if cid not in rtms_map: rtms_map[cid] = set()
    rtms_map[cid].add(r["match_key_area"])

complexes = supabase.table("complexes").select("id, name, complex_no").execute().data

with open("pipeline/naver_complex_mapping.json", "r", encoding="utf-8") as f:
    nmap = json.load(f)

def get_naver_ptps():
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        for idx, c in enumerate([c for c in complexes if '신현대' in c['name']]):
            nid = nmap.get(str(c["complex_no"]))
            if not nid: continue
            cid = c["id"]
            name = c["name"]
            
            page = context.new_page()
            ptps = []
            
            def handle_response(response):
                url = response.url
                if "complex" in url.lower() or "overview" in url.lower():
                    try:
                        data = response.json()
                        data_str = str(data)
                        if "pyeongs" in data_str or "complexPyeongDetailList" in data_str:
                            if "pyeongs" in data:
                                ptps.extend(data["pyeongs"])
                            elif "result" in data and "complexDetail" in data["result"]:
                                ptps.extend(data["result"]["complexDetail"].get("complexPyeongDetailList", []))
                            elif "complexPyeongDetailList" in data:
                                ptps.extend(data["complexPyeongDetailList"])
                    except:
                        pass
            
            page.on("response", handle_response)
            main_url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1,B1,B2"
            try:
                page.goto(main_url, wait_until='networkidle', timeout=10000)
                time.sleep(1.5)
            except:
                pass
            page.close()
            
            if ptps:
                print(f"[{idx+1}/{len(complexes)}] {name} - {len(ptps)} pyeongs.")
                results[cid] = ptps
            else:
                print(f"[{idx+1}/{len(complexes)}] {name} - NO pyeongs found!")
                
        browser.close()
    return results

naver_results = get_naver_ptps()
output = {"mapped": [], "unmapped": {}}

for c in complexes:
    cid = c["id"]
    name = c["name"]
    rtms_areas = sorted(list(rtms_map.get(cid, set())))
    naver_ptps = naver_results.get(cid, [])
    
    matched_rtms = set()
    unmapped_ptps = []
    
    for n in naver_ptps:
        ptp_no = str(n.get("pyeongNo") or n.get("ptpNo"))
        ptp_nm = str(n.get("pyeongName") or n.get("pyeongNm"))
        ex_area = float(n.get("exclusiveArea", 0))
        
        int_area = int(ex_area)
        
        if int_area in rtms_areas:
            output["mapped"].append({
                "complex_id": cid,
                "complex_name": name,
                "naver_ptp_no": ptp_no,
                "pyeong_name": ptp_nm,
                "naver_exclusive_area": ex_area,
                "match_key_area": int_area
            })
            matched_rtms.add(int_area)
        else:
            # Let's see if there is a match with rounded value (+1)
            # Naver 108.31, integer is 108. RTMS is 107. 
            # We want to match Naver 114A (107) -> RTMS 107.
            # If Naver yields 107 for 114A, it matches smoothly.
            unmapped_ptps.append({
                "ptp_no": ptp_no,
                "pyeong_name": ptp_nm,
                "exclusive_area": ex_area
            })
            
    unmapped_rtms = [a for a in rtms_areas if a not in matched_rtms]
    if unmapped_ptps or unmapped_rtms:
        output["unmapped"][name] = {
            "unmapped_rtms": unmapped_rtms,
            "unmapped_naver": unmapped_ptps
        }

with open("pipeline/pyeong_map_result.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("Done! Mapped:", len(output["mapped"]))
print("Has Discrepancies:", len(output["unmapped"]))
