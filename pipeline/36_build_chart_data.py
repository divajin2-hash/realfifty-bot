import os
import json
from collections import defaultdict
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

out_dir = 'web/public/chart_data'
os.makedirs(out_dir, exist_ok=True)

print("Reading kb50_stats.json...")
with open('web/src/data/kb50_stats.json', 'r', encoding='utf-8') as f:
    stats_data = json.load(f)

for complex_data in stats_data:
    cid = complex_data['complex']['id']
    
    # Get daily asks (history) for this complex
    history = []
    offset = 0
    while True:
        chunk = sb.table('daily_history').select('area, base_date, lowest_ask').eq('complex_id', cid).order('base_date').range(offset, offset + 999).execute().data
        if not chunk: break
        history.extend(chunk)
        if len(chunk) < 1000: break
        offset += 1000
        
    asks_by_area = defaultdict(list)
    for h in history:
        asks_by_area[str(h['area'])].append({'date': h['base_date'], 'price': h['lowest_ask']})
        
    final_payload = {}
    
    for s in complex_data['stats']:
        ptp_name = s['pyeong_name']
        integer_area = str(s['match_key_area'])
        
        # Calculate volume per month from trades
        vol_dict = defaultdict(int)
        for t in s.get('all_trades_history', []):
            month = t['date'][:7]
            vol_dict[month] += 1
            
        vol_list = [{'month': m, 'count': c} for m, c in sorted(vol_dict.items())]
        
        final_payload[ptp_name] = {
            'trades': s.get('all_trades_history', []),
            'volume': vol_list,
            'asks': asks_by_area.get(integer_area, []) # Fallback to integer grouping for asks
        }
        
    with open(f"{out_dir}/{cid}.json", 'w', encoding='utf-8') as f:
        json.dump(final_payload, f, ensure_ascii=False)

print("Generated chart JSON files perfectly matched to ptp_name!")
