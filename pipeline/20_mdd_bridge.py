from type_matching import area_key, match_trades
from pathlib import Path
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_mdd_bridge():
    target_date = datetime.now().strftime('%Y-%m-%d')
    json_path = str(Path(__file__).with_name(f"raw_daily_asks_{target_date}.json"))
    
    if not os.path.exists(json_path):
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        daily_asks = json.load(f)
        
    complexes = supabase.table("complexes").select("id, complex_no").execute().data
    cx_map_id = {str(c["complex_no"]): c["id"] for c in complexes}
    
    # 1. 732개 독립 평형 정보 구성
    pyeongs_map = {}
    for ask in daily_asks:
        c_no = ask.get("complex_no")
        if not c_no: continue
        cid = cx_map_id.get(c_no)
        if not cid: continue
        
        ptp_no = str(ask.get("ptp_no", "0"))
        ex_area = float(ask.get("exclusive_area", 0))
        node_key = f"{cid}_{ptp_no}"
        
        # In V3, PTP NO is completely unique per complex.
        import re as _re
        ptp_nm = ask.get("ptp_name", "") or ""
        m = _re.match(r'^(\d+)', ptp_nm)
        supply_area = int(m.group(1)) if m else int(round(ex_area))
        
        pyeongs_map[node_key] = {
            "cid": cid,
            "naver_complex_no": ask["naver_complex_no"],
            "ptp_no": ptp_no,
            "exclusive_area": ex_area,
            "ptp_name": ptp_nm,
            # We keep match_key_area as int for any legacy UI components, but use exact float for matching
            "match_key_area": int(round(ex_area)),
            "pyeong_name": ptp_nm,
            
            "price": ask.get("lowest_ask", 0),
            "normal_lowest_ask": ask.get("normal_lowest_ask", 0),
            "sale_count": ask.get("sale_count", 0),
            "jeonse_count": ask.get("jeonse_count", 0),
            "jeonse_lowest_ask": ask.get("jeonse_lowest_ask", 0),
            "jeonse_rate": ask.get("jeonse_rate", 0),
            "top_5": ask.get("top_5", [])
        }
            
    # 2. 거래내역 로드 (소수점 원본 지원)
    source = os.environ.get("RTMS_VERIFIED_FILE")
    if not source:
        raise RuntimeError("Verified source required; run daily_type_matching first")
    all_trades = json.loads(Path(source).read_text(encoding="utf-8"))["transactions"]
    grouped_ath = {}
    for node_key, p_data in pyeongs_map.items():
        trades = [t for t in all_trades if t["complex_id"] == p_data["cid"]]
        peers = [p for p in pyeongs_map.values() if p["cid"] == p_data["cid"]]
        matched, _ = match_trades(p_data, peers, trades)
        if matched:
            highest = max(matched, key=lambda t: (t["deal_price"], t["deal_date"]))
            grouped_ath[node_key] = {"price": highest["deal_price"], "date": highest["deal_date"]}

    # 4. MDD 결합
    stats_to_insert = []
    for node_key, ask_data in pyeongs_map.items():
        ath = grouped_ath.get(node_key)
        
        ath_price = ath["price"] if ath else 0
        current_ask = ask_data["price"]
        
        mdd = 0
        if ath_price > 0 and current_ask > 0:
            mdd = round(((current_ask - ath_price) / ath_price) * 100, 2)
            
        stats_to_insert.append({
            "complex_id": ask_data["cid"],
            "pyeong_name": ask_data["pyeong_name"],
            "naver_ptp_no": ask_data["ptp_no"],
            "match_key_area": ask_data["match_key_area"],
            "current_lowest_ask": current_ask,
            "highest_deal_price": ath_price,
            "highest_deal_date": ath["date"] if ath else None,
            "mdd_rate": mdd,
            "normal_lowest_ask": ask_data.get("normal_lowest_ask", 0),
            "sale_count": ask_data.get("sale_count", 0),
            "jeonse_count": ask_data.get("jeonse_count", 0),
            "jeonse_lowest_ask": ask_data.get("jeonse_lowest_ask", 0),
            "jeonse_rate": ask_data.get("jeonse_rate", 0),
            "top_5_listings": ask_data.get("top_5", [])
        })
        
    # Upsert preserves the previous snapshot if a subsequent request fails.
    
    if stats_to_insert:
        chunk_size = 500
        for i in range(0, len(stats_to_insert), chunk_size):
            supabase.table("pyeong_stats").upsert(stats_to_insert[i:i+chunk_size], on_conflict="complex_id, naver_ptp_no").execute()

if __name__ == "__main__":
    run_mdd_bridge()
