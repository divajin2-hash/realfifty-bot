import os
import json
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

    print(f"Fetching pyeong_stats...")
    py_stats = fetch_all("pyeong_stats")
    py_map = {}
    for ps in py_stats:
        k = f"{ps['complex_id']}_{ps['match_key_area']}"
        py_map[k] = ps

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

    final_data = []
    current_date_str = "2026-07"

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

        for area, trades in grouped[cid].items():
            trades_sorted = sorted(trades, key=lambda x: x["deal_date"])
            highest_trade = max(trades_sorted, key=lambda x: x["deal_price"])
            
            def map_t(t):
                return {
                    "price": t["deal_price"],
                    "date": t["deal_date"],
                    "floor": t["floor"],
                    "type": "중개거래"
                }

            absolute_recent = map_t(trades_sorted[-1])
            month_deals = [map_t(t) for t in trades_sorted if t["deal_date"].startswith(current_date_str)]
            
            recent_5 = trades_sorted[-5:]
            recent_avg = sum(t["deal_price"] for t in recent_5) / len(recent_5) if recent_5 else 0
            mock_ask = int(recent_avg * 0.98)
            
            # 🔥 찐 네이버 최저 호가 연동 (pyeong_stats)
            real_ask = py_map.get(f"{cid}_{area}", {}).get("current_lowest_ask")
            final_ask = real_ask if real_ask else mock_ask
            
            c_stats.append({
                "match_key_area": area,
                "highest_deal_price": highest_trade["deal_price"],
                "highest_deal_date": highest_trade["deal_date"],
                "recent_deal_absolute": absolute_recent,
                "month_deals": month_deals,
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