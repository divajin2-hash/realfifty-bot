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
    daily_stats = defaultdict(lambda: {'count': 0, 'ath_sum': 0, 'ask_sum': 0})
    for r in rows:
        d = r['base_date']
        if r.get('ath_price') and r.get('lowest_ask'):
            daily_stats[d]['ath_sum'] += r['ath_price']
            daily_stats[d]['ask_sum'] += r['lowest_ask']
            daily_stats[d]['count'] += 1
    macro_data = []
    for date in sorted(daily_stats.keys()):
        stats = daily_stats[date]
        if stats['count'] == 0: continue
        cap_ratio = round((stats['ask_sum'] / stats['ath_sum']) * 100, 2) if stats['ath_sum'] > 0 else 0
        macro_data.append({"date": date, "market_recovery_index": cap_ratio})
    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'macro_index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=2)
    print(f"Macro Index generated: {len(macro_data)} days.")
if __name__ == '__main__':
    run()