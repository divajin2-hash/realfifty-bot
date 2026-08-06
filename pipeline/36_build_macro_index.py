import os, json, statistics
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def run():
    print("Building Macro Index JSON from pyeong_stats (source of truth)...")

    # Step 1: Get ATH per (complex_id, match_key_area) from pyeong_stats - this is cannonical
    ps_rows = []
    offset = 0
    while True:
        res = supabase.table('pyeong_stats').select(
            'complex_id, match_key_area, highest_deal_price, current_lowest_ask'
        ).range(offset, offset + 999).execute()
        if not res.data: break
        ps_rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break

    print(f"pyeong_stats rows: {len(ps_rows)}")

    # Step 2: Build canonical ATH map: (complex_id, match_key_area) -> ath_price
    ath_map = {}
    for r in ps_rows:
        key = (r['complex_id'], r['match_key_area'])
        ath = r.get('highest_deal_price')
        if ath and ath > 100000000:
            ath_map[key] = ath

    # Step 3: Get daily snapshots per day from daily_history
    # We need base_date, complex_id (via complex_name), match_key_area, lowest_ask
    # But daily_history doesn't have complex_id. Let's get complex id map from complexes table
    cx_res = supabase.table('complexes').select('id, name').execute()
    name_to_id = {r['name']: r['id'] for r in cx_res.data}

    # Step 4: Get all daily_history rows
    dh_rows = []
    offset = 0
    while True:
        res = supabase.table('daily_history').select(
            'base_date, complex_name, area, lowest_ask'
        ).range(offset, offset + 999).execute()
        if not res.data: break
        dh_rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break

    print(f"daily_history rows: {len(dh_rows)}")

    # Step 5: Calculate drop rate per date using correct ATH
    daily_rates = defaultdict(list)
    for r in dh_rows:
        d = r['base_date']
        ask = r.get('lowest_ask')
        if not ask or ask <= 0:
            continue
        cx_id = name_to_id.get(r['complex_name'])
        if not cx_id:
            continue
        area = r.get('area')
        key = (cx_id, area)
        ath = ath_map.get(key)
        if not ath or ath <= 0:
            continue
        # Sanity check: ath must be at least 30% of ask, and not more than 3x ask
        if ath < ask * 0.3 or ath > ask * 3:
            continue
        drop_rate = ((ask - ath) / ath) * 100
        daily_rates[d].append(drop_rate)

    macro_data = []
    for date in sorted(daily_rates.keys()):
        rates = daily_rates[date]
        if len(rates) < 20: continue
        median_drop = round(statistics.median(rates), 2)
        macro_data.append({
            "date": date,
            "avg_drop_rate": median_drop,
            "market_recovery_index": round(100 + median_drop, 2),
            "sample_count": len(rates)
        })

    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'macro_index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(macro_data, f, ensure_ascii=False, indent=2)

    print(f"\nMacro Index generated: {len(macro_data)} days")
    for m in macro_data:
        print(f"  {m['date']}: {m['avg_drop_rate']:+.2f}% (n={m['sample_count']}) => Index {m['market_recovery_index']}%")

if __name__ == '__main__':
    run()