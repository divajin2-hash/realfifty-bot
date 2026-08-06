import os, json
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def run():
    print("Building Macro Index JSON...")
    rows, offset = [], 0
    while True:
        res = supabase.table('daily_history').select('base_date, ath_price, lowest_ask').range(offset, offset + 999).execute()
        if not res.data: break
        rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break
        
    daily_stats = defaultdict(lambda: {'drop_sum': 0, 'count': 0})
    for r in rows:
        d = r['base_date']
        if r.get('ath_price') and r.get('lowest_ask'):
            # ONLY count if ath_price is reasonable to avoid corrupted historical zeros
            if r['ath_price'] > 100000000:
                drop_rate = ((r['lowest_ask'] - r['ath_price']) / r['ath_price']) * 100
                daily_stats[d]['drop_sum'] += drop_rate
                daily_stats[d]['count'] += 1
                
    macro_data = []
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        if stats['count'] == 0: continue
        avg_drop = round(stats['drop_sum'] / stats['count'], 2)
        # Normal market recovery index should roughly be 100 + avg_drop
        macro_data.append({"date": date, "avg_drop_rate": avg_drop, "market_recovery_index": round(100 + avg_drop, 2)})
        
    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'macro_index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=2)
        
    print(f"Macro Index generated: {len(macro_data)} days.")

if __name__ == '__main__':
    run()