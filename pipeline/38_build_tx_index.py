import os, json, statistics
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def run():
    print("Building Macro Transaction Index (monthly real deal vs ATH)...")

    # Step 1: Get ATH per (complex_id, match_key_area) from pyeong_stats
    ps_rows = []
    offset = 0
    while True:
        res = supabase.table('pyeong_stats').select(
            'complex_id, match_key_area, highest_deal_price'
        ).range(offset, offset + 999).execute()
        if not res.data: break
        ps_rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break

    ath_map = {}
    for r in ps_rows:
        key = (r['complex_id'], r['match_key_area'])
        ath = r.get('highest_deal_price')
        if ath and ath > 100000000:
            ath_map[key] = ath

    print(f"  ATH map: {len(ath_map)} types loaded")

    # Step 2: Get all rtms_transactions
    tx_rows = []
    offset = 0
    while True:
        res = supabase.table('rtms_transactions').select(
            'complex_id, match_key_area, deal_date, deal_price, transaction_type'
        ).range(offset, offset + 999).execute()
        if not res.data: break
        tx_rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break

    print(f"  Transactions: {len(tx_rows)} rows")

    # Step 3: Group by month, calculate (deal_price / ath) ratio per transaction
    # Skip reconstructed/jeonse deals
    monthly_ratios = defaultdict(list)
    for r in tx_rows:
        # Skip jeonse (전세) or reconstruction deals
        ttype = (r.get('transaction_type') or '').strip()
        if ttype in ['전세', '전세(임대)', '재건축']:
            continue
        
        deal_date = r.get('deal_date', '')
        if not deal_date or len(deal_date) < 7:
            continue
        
        month = deal_date[:7]  # YYYY-MM
        
        key = (r['complex_id'], r['match_key_area'])
        ath = ath_map.get(key)
        price = r.get('deal_price')
        
        if not ath or not price or price <= 0:
            continue
        
        # Sanity check: skip if price is unreasonably far from ATH
        ratio = (price / ath) * 100
        if ratio < 20 or ratio > 200:  # skip obviously wrong data
            continue
        
        monthly_ratios[month].append(ratio)

    # Step 4: Build timeline
    macro_tx = []
    for month in sorted(monthly_ratios.keys()):
        ratios = monthly_ratios[month]
        if len(ratios) < 5:  # Need at least 5 transactions to be meaningful
            continue
        median_ratio = round(statistics.median(ratios), 2)
        macro_tx.append({
            "month": month,
            "recovery_rate": median_ratio,  # % of ATH
            "sample_count": len(ratios)
        })

    print(f"  Timeline: {len(macro_tx)} months")
    
    # Print last 12 for inspection
    for m in macro_tx[-12:]:
        print(f"    {m['month']}: {m['recovery_rate']}% of ATH (n={m['sample_count']})")

    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'macro_tx_index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(macro_tx, f, ensure_ascii=False, indent=2)

    print(f"\nSaved: {out_path}")

if __name__ == '__main__':
    run()
