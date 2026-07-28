import os
import sys
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
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

    # Prepare data insertion using KST
    KST = timezone(timedelta(hours=9))
    
    # Check if a custom date is provided as argument for manual backfill
    today_str = datetime.now(KST).strftime('%Y-%m-%d')
    if len(sys.argv) > 1:
        today_str = sys.argv[1]
        print(f"⚠️ Using custom date: {today_str}")

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

            record = {
                "complex_id": c_id,
                "complex_name": c_name,
                "area": area,
                "base_date": today_str,
                "ath_price": ath,
                "recent_price": recent,
                "month_volume": vol,
                "lowest_ask": ask
            }
            records.append(record)

    if not records:
        print("⚠️ No records to insert.")
        return
        
    print(f"✅ Prepared {len(records)} daily snapshots for {today_str}!")
    
    # Upsert to DB
    print("🚀 Upserting to daily_history in Supabase (1000 chunk limit)...")
    
    # Insert in chunks of 500
    chunk_size = 500
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        res = supabase.table("daily_history").upsert(chunk, on_conflict="complex_id, area, base_date").execute()
        print(f"✔️ Chunk {i // chunk_size + 1} pushed! ({len(chunk)} records)")

    print("🎉 Daily bot execution complete! One day's real snapshot is recorded.")

if __name__ == "__main__":
    run()
