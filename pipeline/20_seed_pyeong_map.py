import os
import sys
import time
import json
import re
import io
from dotenv import load_dotenv
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def parse_korean_price_to_int(p_str):
    p_str = p_str.replace(' ', '').replace(',', '')
    if '억' in p_str:
        parts = p_str.split('억')
        eok = int(parts[0]) * 100000000
        man_digits = re.sub(r'[^0-9]', '', parts[1])
        man = int(man_digits) * 10000 if man_digits else 0
        return eok + man
    elif '만' in p_str:
        return int(re.sub(r'[^0-9]', '', p_str)) * 10000
    return int(re.sub(r'[^0-9]', '', p_str)) * 10000

def get_rtms_trades(complex_id):
    res = supabase.table('rtms_transactions').select('*').eq('complex_id', complex_id).execute()
    return res.data

def run_mapping():
    print("🔥 Starting Pyeong Map Generator (Cross Validation)...")
    complexes = supabase.table('complexes').select('*').execute().data
    with open('pipeline/naver_complex_mapping.json', 'r', encoding='utf-8') as f:
        nmap = json.load(f)
    rev_nmap = {}
    for db_cno, nids in nmap.items():
        cid = [c['id'] for c in complexes if str(c['complex_no']) == str(db_cno)][0]
        if isinstance(nids, str): nids = [nids]
        for nid in nids:
            rev_nmap[str(nid)] = cid
            
    import glob
    ask_files = glob.glob('pipeline/raw_daily_asks_*.json')
    ask_files.sort()
    with open(ask_files[-1], 'r', encoding='utf-8') as f:
        daily_asks = json.load(f)

    target_asks = []
    seen_ptps = set()
    for ask in daily_asks:
        key = f"{ask['naver_complex_no']}_{ask['ptp_no']}"
        if key not in seen_ptps:
            target_asks.append(ask)
            seen_ptps.add(key)
            
    print(f"Found {len(target_asks)} PTPs to map.")
    map_path = 'pipeline/pyeong_map_result.json'
    if os.path.exists(map_path):
        with open(map_path, 'r', encoding='utf-8') as f:
            final_map = json.load(f)
    else:
        final_map = {}
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        current_cid = None
        context = None
        rtms_trades = []
        
        for ask in target_asks:
            nid = str(ask['naver_complex_no'])
            ptp_no = str(ask['ptp_no'])
            cid = rev_nmap.get(nid)
            ptp_name = ask.get('ptp_name', '')
            ex_area = ask.get('exclusive_area', 0)
            
            if not cid: continue
            node_key = f"{cid}_{nid}_{ptp_no}"
            if node_key in final_map:
                continue
                
            if current_cid != cid:
                current_cid = cid
                rtms_trades = get_rtms_trades(cid)
                if context: context.close()
                context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
                context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            print(f"\n🏢 {ask['complex_name']} - {ptp_name} ({ptp_no}) ExArea: {ex_area}")
            page = context.new_page()
            url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1&ptpNo={ptp_no}"
            found_match_key = None
            try:
                page.goto(url, wait_until='networkidle', timeout=15000)
                page.wait_for_selector("#detailContents3", timeout=5000)
                page.click("#detailContents3")
                time.sleep(1.5)
                rows = page.locator(".detail_data_table.table_real_price tbody tr").all()
                if rows:
                    for row in rows[:5]:
                        cells = row.locator("th, td").all()
                        if len(cells) >= 3:
                            dt_raw = cells[0].inner_text().strip()
                            price_raw = cells[1].inner_text().strip()
                            floor_raw = cells[2].inner_text().strip()
                            if '.' not in dt_raw: continue
                            yy, mm, dd = dt_raw.split('.')
                            yy = '20' + yy if len(yy)==2 else yy
                            deal_date = f"{yy}-{mm.zfill(2)}-{dd.zfill(2)}"
                            price_int = parse_korean_price_to_int(price_raw)
                            flor = re.sub(r'[^0-9]', '', floor_raw)
                            floor_int = int(flor) if flor else None
                            matches = [t for t in rtms_trades if t['deal_date'] == deal_date and t['deal_price'] == price_int]
                            if matches:
                                f_match = next((t for t in matches if t['floor'] == floor_int), matches[0])
                                found_match_key = f_match['match_key_area']
                                print(f"  ✅ Matched! Naver deal {deal_date} {price_raw} -> DB match_key_area: {found_match_key}")
                                break
            except Exception as e:
                print(f"  ⚠️ Error scraping deals: {e}")
            finally:
                page.close()
                
            if not found_match_key:
                found_match_key = int(round(ex_area))
                print(f"  ⚠️ No trades found/matched. Fallback to heuristic: {found_match_key}")
                
            final_map[node_key] = {
                'cid': cid,
                'nid': nid,
                'ptp_no': ptp_no,
                'ptp_name': ptp_name,
                'match_key_area': found_match_key,
                'supply_area': ask['supply_area'],
                'exclusive_area': ex_area
            }
            with open(map_path, 'w', encoding='utf-8') as f:\
                json.dump(final_map, f, ensure_ascii=False, indent=2)
                
        if context: context.close()
        browser.close()
    print("Done creating pyeong_map_result.json!")

if __name__ == '__main__':
    run_mapping()
