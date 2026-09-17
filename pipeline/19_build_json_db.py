from type_matching import match_trades
import os
import json
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_all(table):
    all_data = []
    limit = 1000
    offset = 0
    while True:
        res = supabase.table(table).select("*").range(offset, offset + limit - 1).execute()
        data = res.data
        if not data:
            break
        all_data.extend(data)
        if len(data) < limit:
            break
        offset += limit
        print(f"Fetched {len(all_data)} rows from {table}...")
    return all_data

def build_db():
    print("Fetching complexes...")
    complexes = fetch_all("complexes")
    
    import glob
    import sys
    
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
        target_file = f'pipeline/raw_daily_asks_{target_date}.json'
        print(f"Using specific raw asks file: {target_file}")
        with open(target_file, 'r', encoding='utf-8') as f:
            daily_asks = json.load(f)
    else:
        ask_files = glob.glob(os.path.join(os.path.dirname(__file__), 'raw_daily_asks_*.json'))
        ask_files.sort()
        print(f"Using latest raw asks file: {ask_files[-1]}")
        with open(ask_files[-1], 'r', encoding='utf-8') as f:
            daily_asks = json.load(f)
        
    # Map complex_no to id
    cx_map_id = {str(c["complex_no"]): str(c["id"]) for c in complexes}
    
    # Group asks by complex_id
    asks_by_cid = {}
    valid_areas_map = {}
    for ask in daily_asks:
        cid = cx_map_id.get(str(ask.get("complex_no")))
        if not cid: continue
        if cid not in asks_by_cid: asks_by_cid[cid] = []
        asks_by_cid[cid].append(ask)
        
        area = int(round(ask.get('exclusive_area', 0)))
        if cid == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(ask.get('exclusive_area', 0) - 82.23) < 0.01:
            area = 83
        if cid not in valid_areas_map: valid_areas_map[cid] = set()
        valid_areas_map[cid].add(area)


    print(f"Fetching rtms_transactions...")
    transactions = fetch_all("rtms_transactions")
    cached_path = os.path.join(os.path.dirname(__file__), 'rtms_recheck', 'verified.json')
    if os.path.exists(cached_path):
        with open(cached_path, encoding='utf-8') as source:
            recovered = json.load(source)
        index = {}
        for t in recovered['transactions']:
            key = (str(t['complex_id']), t['deal_date'], t['deal_price'], t.get('floor'))
            index.setdefault(key, set()).add(str(t['exclusive_area_exact']))
        recovered_count = 0
        for t in transactions:
            if t.get('exclusive_area_exact') is not None:
                continue
            key = (str(t['complex_id']), t['deal_date'], t['deal_price'], t.get('floor'))
            candidates = index.get(key, set())
            if len(candidates) == 1:
                t['exclusive_area_exact'] = float(next(iter(candidates)))
                recovered_count += 1
        print(f'Recovered original areas by unique date/price/floor key: {recovered_count}')
    verified_path = os.environ.get('RTMS_VERIFIED_FILE')
    if verified_path:
        with open(verified_path, encoding='utf-8') as source:
            verified = json.load(source)
        # Replace the verified interval, including cancellations; retain older history separately.
        start = verified['from_month'][:4] + '-' + verified['from_month'][4:] + '-01'
        end_month = verified['to_month'][:4] + '-' + verified['to_month'][4:]
        transactions = [t for t in transactions if t['deal_date'] < start or t['deal_date'][:7] > end_month] + verified['transactions']
        print(f"Applied verified official interval: {start} to {end_month}")

    grouped = {str(c['id']): [] for c in complexes}
    for record_index, t in enumerate(transactions):
        t['_record_id'] = str(t.get('id') or f'raw-{record_index}')
        if str(t['complex_id']) in grouped:
            grouped[str(t['complex_id'])].append(t)

    final_data = []
    now = datetime.now()
    # Rolling 30 days window for volume
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    for c in complexes:
        cid = str(c["id"])
        c_stats = []
        
        # UI uses Naver PTP directly
        asks = asks_by_cid.get(cid, [])
        asks = list({(str(a.get("naver_complex_no")),str(a.get("ptp_no"))): a for a in asks}.values())
        for ask in asks:
            area = int(round(ask.get('exclusive_area', 0)))
            if cid == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(ask.get('exclusive_area', 0) - 82.23) < 0.01:
                area = 83
                
            trades_to_use, match = match_trades(ask, asks, grouped.get(cid, []))

            if trades_to_use:
                trades_sorted = sorted(trades_to_use, key=lambda x: x["deal_date"])
                highest_trade = max(trades_sorted, key=lambda x: x["deal_price"])
                
                def map_t(t):
                    return {
                        "id": t["_record_id"],
                        "price": t["deal_price"],
                        "date": t["deal_date"],
                        "floor": t.get("floor"),
                        "exclusive_area_exact": t.get("exclusive_area_exact"),
                        "type": t.get("transaction_type") or "거래 구분 미확인"
                    }

                absolute_recent = map_t(trades_sorted[-1])
                month_deals = [map_t(t) for t in trades_sorted if t["deal_date"] >= thirty_days_ago]
                all_trades_history = [map_t(t) for t in trades_sorted]
                
                h_price = highest_trade["deal_price"]
                h_date = highest_trade["deal_date"]
            else:
                absolute_recent = None
                month_deals = []
                all_trades_history = []
                h_price = 0
                h_date = None
                
            final_ask = ask.get('lowest_ask', 0)
            
            c_stats.append({
                "match_key_area": area,
                "transaction_match": match,
                "pyeong_name": ask.get("ptp_name", ""),
                "naver_ptp_no": ask.get("ptp_no"),
                "naver_complex_no": ask.get("naver_complex_no"),
                "exclusive_area": ask.get("exclusive_area"),
                "supply_area": ask.get("supply_area"),
                "highest_deal_price": h_price,
                "highest_deal_date": h_date,
                "recent_deal_absolute": absolute_recent,
                "month_deals": month_deals,
                "all_trades_history": all_trades_history,
                "month_volume": len(month_deals),
                "max_month_volume": 10,
                "volume_drop_rate": 0,
                "current_lowest_ask": final_ask,
                
                # --- V2 Extra Fields ---
                "normal_lowest_ask": ask.get("normal_lowest_ask", 0),
                "sale_count": ask.get("sale_count", 0),
                "jeonse_count": ask.get("jeonse_count", 0),
                "jeonse_lowest_ask": ask.get("jeonse_lowest_ask", 0),
                "jeonse_rate": ask.get("jeonse_rate", 0),
                "top_5_listings": ask.get("top_5", [])
            })
            
        final_data.append({
            "complex": {
                "id": cid,
                "name": c["name"],
                "address": c.get("region", "")
            },
            "stats": c_stats
        })

    generated_at = datetime.now(timezone.utc).isoformat()
    for group in final_data:
        group["generated_at"] = generated_at
        group["matching_version"] = "area-v3"

    out_path = os.path.join("web", "src", "data", "kb50_stats.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    try:
        os.replace(out_path + ".tmp", out_path)
    except PermissionError:
        # Windows dev-server file handles may deny replacement of an open file.
        with open(out_path + '.tmp', 'rb') as source, open(out_path, 'wb') as destination:
            destination.write(source.read())
        os.remove(out_path + '.tmp')
    from build_daily_changes import run as build_changes
    build_changes()
    print(f"Generated DB at {out_path} with {len(final_data)} complexes.")

if __name__ == "__main__":
    build_db()