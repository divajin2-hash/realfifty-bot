import json, os
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('pipeline/.env')
sb = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

asks = json.load(open('pipeline/raw_daily_asks_2026-07-28.json', 'r', encoding='utf-8'))
c_map = {str(c['complex_no']): c['id'] for c in sb.table('complexes').select('id, complex_no').execute().data}

naver_areas = {}
for ask in asks:
    c_no = ask.get('complex_no')
    cid = c_map.get(str(c_no))
    if not cid: continue
    area = int(round(float(ask.get('exclusive_area', 0))))
    if cid not in naver_areas: naver_areas[cid] = set()
    naver_areas[cid].add(area)

rtms = sb.table('rtms_transactions').select('complex_id, match_key_area').execute().data
rtms_areas = {}
for r in rtms:
    cid = r['complex_id']
    if cid not in rtms_areas: rtms_areas[cid] = set()
    rtms_areas[cid].add(r['match_key_area'])

cx = sb.table('complexes').select('id, name').execute().data
cid_to_name = {c['id']: c['name'] for c in cx}
mismatches = []
for cid, r_areas in rtms_areas.items():
    n_areas = naver_areas.get(cid, set())
    unmatched = [a for a in r_areas if a not in n_areas]
    if unmatched:
        mismatches.append(f"[{cid_to_name.get(cid, 'Unknown')}] Missing Naver Pyeongs for RTMS Deals: {unmatched}")

for m in mismatches: print(m)
print(f"Total Complexes with missing Pyeongs: {len(mismatches)}")
