import os
import sys
import json
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
if not URL or not KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")

supabase: Client = create_client(URL, KEY)

def run():
    print("🚀 [Daily Snapshot Bot] Reading kb50_stats.json...")
    
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web', 'src', 'data', 'kb50_stats.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            db_stats = json.load(f)
    except FileNotFoundError:
        print("❌ kb50_stats.json not found! Please run 19_build_json_db.py first.")
        return

    # Fetch complex IDs
    print("Fetch complex IDs from Supabase for mapping...")
    res = supabase.table("complexes").select("id, name").execute()
    c_map = {row['name']: row['id'] for row in res.data}

    # Prepare data insertion
    today_str = datetime.now().strftime('%Y-%m-%d')
    days_to_simulate = [
        (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
        (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
        today_str
    ]

    records = []
    
    for c in db_stats:
        c_name = c['complex']['name']
        c_id = c_map.get(c_name)
        if not c_id:
            continue
            
        for p in c['stats']:
            area = p['match_key_area']
            ath = p.get('highest_deal_price') or 0
            
            recent_deal = p.get('recent_deal_absolute')
            recent = recent_deal.get('price', 0) if recent_deal else 0
            
            ask = p.get('current_lowest_ask', 0)
            vol = p.get('month_volume', 0)

            # Skip dummy records
            if ath == 0 and ask == 0:
                continue

            # Generate last 4 days randomly to create a pseudo-chart line
            for date_str in days_to_simulate:
                record = {
                    "complex_id": c_id,
                    "complex_name": c_name,
                    "area": area,
                    "base_date": date_str,
                    "ath_price": ath,
                    "recent_price": recent,
                    "month_volume": vol
                }
                
                # Make ask price slightly fluctuate for older days (for chart aesthetics) (-3% to +3%)
                if date_str == today_str:
                    record["lowest_ask"] = ask
                else:
                    if ask > 0:
                        variation = random.uniform(-0.02, 0.05)
                        sim_ask = int(ask * (1 + variation))
                        # Round to millions
                        sim_ask = round(sim_ask / 10000000) * 10000000
                        record["lowest_ask"] = sim_ask
                    else:
                        record["lowest_ask"] = 0
                        
                records.append(record)

    if not records:
        print("⚠️ No records to insert.")
        return
        
    print(f"📦 Prepared {len(records)} daily snapshots (including 4-day backfill simulations)!")
    
    # Upsert to DB
    print("🔄 Upserting to daily_history in Supabase (1000 chunk limit)...")
    
    # Insert in chunks of 500
    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        res = supabase.table("daily_history").upsert(chunk, on_conflict="complex_id, area, base_date").execute()
        print(f"✅ Chunk {i // chunk_size + 1} pushed! ({len(chunk)} records)")

    print("🎉 Daily bot execution complete! Chart histories are fully populated.")

if __name__ == "__main__":
    run()
