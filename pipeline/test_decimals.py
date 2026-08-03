import json
from dotenv import load_dotenv
import os
from supabase import create_client
load_dotenv('pipeline/.env')
sp=create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def fetch_all(table, columns='*'):
    all_data = []
    limit = 1000
    offset = 0
    while True:
        res = sp.table(table).select(columns).range(offset, offset + limit - 1).execute()
        data = res.data
        if not data: break
        all_data.extend(data)
        if len(data) < limit: break
        offset += limit
    return all_data

c = fetch_all('complexes', 'id, complex_no, name')
cmap = {str(x['complex_no']): str(x['id']) for x in c}

r = fetch_all('rtms_transactions', 'complex_id, exclusive_area_exact, match_key_area')
rtms_areas = {}
for t in r:
    if not t['exclusive_area_exact']: continue
    cid = str(t['complex_id'])
    if cid not in rtms_areas: rtms_areas[cid] = set()
    rtms_areas[cid].add((float(t['exclusive_area_exact']), t['match_key_area']))

import glob
ask_files = glob.glob('pipeline/raw_daily_asks_*.json')
ask_files.sort()
asks = json.load(open(ask_files[-1], encoding='utf-8'))

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
        unmatch.append((a['complex_name'], a['ptp_name'], a_ex, list(rt)))

print(f'{n_match}/{n_tot} matched exactly!')
if unmatch:
    print('Unmatched examples:', unmatch[:2])
