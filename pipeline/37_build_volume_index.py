import os, json
from supabase import create_client
from dotenv import load_dotenv
from collections import defaultdict
from datetime import datetime

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def run():
    print(" Building Macro Volume Index JSON...")
    
    # We need to fetch all deal_date from rtms_transactions
    rows = []
    offset = 0
    while True:
        res = supabase.table('rtms_transactions').select('deal_date').range(offset, offset + 999).execute()
        if not res.data: break
        rows.extend(res.data)
        offset += 1000
        if len(res.data) < 1000: break
        
    if not rows:
        print("No transactions found.")
        return
        
    month_counts = defaultdict(int)
    for r in rows:
        deal_date = r['deal_date'] 
        month_str = deal_date[:7] # YYYY-MM
        month_counts[month_str] += 1
        
    # Find all time high month
    ath_month = max(month_counts, key=month_counts.get)
    ath_count = month_counts[ath_month]
    print(f" ATH Volume Month: {ath_month} with {ath_count} trades")
    
    # We want the last 24 months for the chart
    sorted_months = sorted(month_counts.keys())
    # Make sure we show up to current month even if 0 (though rtms always has some)
    recent_months = sorted_months[-24:]
    
    macro_volume_data = []
    for m in recent_months:
        count = month_counts[m]
        macro_volume_data.append({
            "month": m,
            "trade_count": count,
            "volume_ratio": round((count / ath_count) * 100, 1)
        })
        
    output_data = {
        "ath_month": ath_month,
        "ath_count": ath_count,
        "timeline": macro_volume_data
    }
        
    out_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'macro_volume_index.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
        
    print(f" Macro Volume Index generated: {out_path}")

if __name__ == '__main__':
    run()
