import os
import json
from collections import defaultdict
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# 1. Ensure output dir
out_dir = 'web/public/chart_data'
os.makedirs(out_dir, exist_ok=True)

print("Fetching complexes...")
c_res = sb.table('complexes').select('id, name').execute().data

for c in c_res:
    cid = c['id']
    # print(f"Processing {c['name']}...")
    
    # trades (Pagination to bypass 1000 limit)
    trades = []
    offset = 0
    while True:
        chunk = sb.table('rtms_transactions').select('match_key_area, deal_date, deal_price').eq('complex_id', cid).order('deal_date').range(offset, offset + 999).execute().data
        if not chunk: break
        trades.extend(chunk)
        if len(chunk) < 1000: break
        offset += 1000
    
    # daily asks (history) limit bypass
    history = []
    offset = 0
    while True:
        chunk = sb.table('daily_history').select('area, base_date, lowest_ask').eq('complex_id', cid).order('base_date').range(offset, offset + 999).execute().data
        if not chunk: break
        history.extend(chunk)
        if len(chunk) < 1000: break
        offset += 1000
    
    # Valid areas from pyeong_stats
    py_stats = sb.table('pyeong_stats').select('match_key_area').eq('complex_id', cid).execute().data
    valid_areas = set(int(ps['match_key_area']) for ps in py_stats)
    
    def resolve_area(area_val):
        area = int(area_val)
        if not valid_areas or area in valid_areas:
            return str(area)
        
        closest = None
        min_diff = 999
        for va in valid_areas:
            diff = abs(va - area)
            if diff < min_diff and diff <= 2:
                min_diff = diff
                closest = va
        
        return str(closest) if closest is not None else str(area)
    
    # Build payload: { '82': { 'trades': [{date, price}], 'volume': [{month, count}], 'asks': [{date, price}] } }
    payload = defaultdict(lambda: {'trades': [], 'volume': defaultdict(int), 'asks': []})
    
    for t in trades:
        k = resolve_area(t['match_key_area'])
        payload[k]['trades'].append({'date': t['deal_date'], 'price': t['deal_price']})
        
        # Volume
        month = t['deal_date'][:7] # YYYY-MM
        payload[k]['volume'][month] += 1
        
    for h in history:
        k = resolve_area(h['area'])
        payload[k]['asks'].append({'date': h['base_date'], 'price': h['lowest_ask']})
        
    # Finalize format
    final_payload = {}
    for k, v in payload.items():
        vol_list = [{'month': m, 'count': c} for m, c in sorted(v['volume'].items())]
        final_payload[k] = {
            'trades': v['trades'],
            'volume': vol_list,
            'asks': v['asks']
        }
        
    with open(f"{out_dir}/{cid}.json", 'w', encoding='utf-8') as f:
        json.dump(final_payload, f, ensure_ascii=False)

print("Generated chart JSON files for all complexes!")
