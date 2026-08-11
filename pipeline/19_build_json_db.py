import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv("pipeline/.env")

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
        ask_files = glob.glob('pipeline/raw_daily_asks_*.json')
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

    grouped = {}
    for c in complexes:
        grouped[str(c["id"])] = {}
    
    for t in transactions:
        c_id = str(t["complex_id"])
        if c_id not in grouped:
            continue
        
        area = int(round(float(t["match_key_area"])))
        if area not in grouped[c_id]:
            grouped[c_id][area] = []
        
        grouped[c_id][area].append(t)

    # ---------------------------------------------------------
    # 오차 면적 병합 (Merge orphaned areas into valid Naver areas)
    # 국토부 실거래가는 59, 84 인데 네이버 호가는 60, 85 인 경우
    # ---------------------------------------------------------
    for cid in list(grouped.keys()):
        valid_areas = valid_areas_map.get(cid, set())
        if not valid_areas:
            continue
            
        for area in list(grouped[cid].keys()):
            if area not in valid_areas:
                closest = None
                min_diff = 999
                for va in valid_areas:
                    diff = abs(va - area)
                    if diff < min_diff and diff <= 2:
                        min_diff = diff
                        closest = va
                        
                if closest is not None:
                    if closest not in grouped[cid]:
                        grouped[cid][closest] = []
                    grouped[cid][closest].extend(grouped[cid][area])
                    del grouped[cid][area]
    # ---------------------------------------------------------

    final_data = []
    now = datetime.now()
    # Rolling 30 days window for volume
    thirty_days_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d")

    for c in complexes:
        cid = str(c["id"])
        c_stats = []
        
        if cid not in grouped or len(grouped[cid]) == 0:
            final_data.append({
                "complex": {
                    "id": cid,
                    "name": c["name"],
                    "address": c.get("region", "")
                },
                "stats": [{
                    'match_key_area': 84,
                    'pyeong_name': "84",
                    'highest_deal_price': 0,
                    'highest_deal_date': None,
                    'recent_deal_absolute': None,
                    'month_deals': [],
                    'month_volume': 0,
                    'max_month_volume': 0,
                    'volume_drop_rate': 0,
                    'current_lowest_ask': 0
                }]
            })
            continue

        # UI uses Naver PTP directly
        asks = asks_by_cid.get(cid, [])
        for ask in asks:
            area = int(round(ask.get('exclusive_area', 0)))
            if cid == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(ask.get('exclusive_area', 0) - 82.23) < 0.01:
                area = 83
                
            all_trades_in_group = grouped[cid].get(area, [])
            if not all_trades_in_group:
                continue
                
            a_ex = float(ask.get('exclusive_area', 0))
            exact_trades = []
            
            # Count how many distinct exclusive areas exist in Naver for this integer group
            group_a_ex_set = set(float(a.get('exclusive_area', 0)) for a in asks if int(round(float(a.get('exclusive_area', 0)))) == area)
            
            for t in all_trades_in_group:
                t_ex = t.get('exclusive_area_exact')
                if t_ex is not None:
                    # Nearest Neighbor matching to handle systematic Naver-MOLIT decimal mismatches 
                    # (e.g. Raemian Schur 84.94 vs 84.946, gap ~0.006)
                    closest_g_a = None
                    min_diff = 999
                    for g_a in group_a_ex_set:
                        diff = abs(float(t_ex) - g_a)
                        if diff < min_diff:
                            min_diff = diff
                            closest_g_a = g_a
                    
                    if closest_g_a is not None and abs(closest_g_a - a_ex) < 1e-5 and min_diff < 0.09:
                        exact_trades.append(t)
                else:
                    exact_trades.append(t)
                        
            if len(group_a_ex_set) > 1:
                # When twins exist, we rely entirely on nearest neighbor partitioning
                trades_to_use = exact_trades
            else:
                trades_to_use = all_trades_in_group
                
            if trades_to_use:
                trades_sorted = sorted(trades_to_use, key=lambda x: x["deal_date"])
                highest_trade = max(trades_sorted, key=lambda x: x["deal_price"])
                
                def map_t(t):
                    return {
                        "price": t["deal_price"],
                        "date": t["deal_date"],
                        "floor": t["floor"],
                        "type": "중개거래"
                    }

                absolute_recent = map_t(trades_sorted[-1])
                month_deals = [map_t(t) for t in trades_sorted if t["deal_date"] >= thirty_days_ago]
                all_trades_history = [{"date": t["deal_date"], "price": t["deal_price"]} for t in trades_sorted]
                
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
                "pyeong_name": ask.get("ptp_name", ""),
                "highest_deal_price": h_price,
                "highest_deal_date": h_date,
                "recent_deal_absolute": absolute_recent,
                "month_deals": month_deals,
                "all_trades_history": all_trades_history,
                "month_volume": len(month_deals),
                "max_month_volume": 10,
                "volume_drop_rate": 0,
                "current_lowest_ask": final_ask
            })
            
        final_data.append({
            "complex": {
                "id": cid,
                "name": c["name"],
                "address": c.get("region", "")
            },
            "stats": c_stats
        })

    out_path = os.path.join("web", "src", "data", "kb50_stats.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"Generated DB at {out_path} with {len(final_data)} complexes.")

if __name__ == "__main__":
    build_db()