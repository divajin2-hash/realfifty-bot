import json
from dotenv import load_dotenv
import os
from supabase import create_client
load_dotenv('pipeline/.env')
sp=create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

c = sp.table('complexes').select('id, complex_no').execute()
cmap = {str(x['complex_no']): str(x['id']) for x in c.data}

r = sp.table('rtms_transactions').select('complex_id, exclusive_area_exact, match_key_area').execute()
rtms_areas = {}
for t in r.data:
    cid = str(t['complex_id'])
    if cid not in rtms_areas: rtms_areas[cid] = set()
    rtms_areas[cid].add((t['exclusive_area_exact'], t['match_key_area']))

asks = json.load(open('pipeline/raw_daily_asks_2026-07-30.json', encoding='utf-8'))
n_tot = 0
n_match = 0
unmatch = []

for a in asks:
    a_ex = float(a['exclusive_area'])
    c_no = str(a['complex_no'])
    cid = cmap.get(c_no)
    if not cid: continue
    n_tot += 1
    rt = rtms_areas.get(cid, set())
    found = False
    for r_ex, r_key in rt:
        if abs(r_ex - a_ex) < 0.05:
            found = True
            n_match += 1
            break
    if not found:
        unmatch.append((a['complex_name'], a['ptp_name'], a_ex, rt))

print(f'{n_match}/{n_tot} matched exactly!')
if unmatch:
    print('Unmatched examples:', unmatch[:3])
