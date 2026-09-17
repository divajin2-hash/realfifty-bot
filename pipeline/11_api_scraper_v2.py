import os
import json
import time
import random
from datetime import datetime
from curl_cffi import requests
from dotenv import load_dotenv
from supabase import create_client

current_dir = os.path.dirname(__file__)
load_dotenv(os.path.join(current_dir, ".env"))
supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

today_str = datetime.now().strftime("%Y-%m-%d")

def fetch_top_listings(session, nid, ptp_no, trade_type="A1"):
    url = "https://fin.land.naver.com/front-api/v1/complex/article/list"
    payload = {
        "size": 30,
        "complexNumber": int(nid),
        "tradeTypes": [trade_type],
        "pyeongTypes": [str(ptp_no)],
        "dongNumbers": [],
        "articleSortType": "PRICE_ASC",
        "lastInfo": [],
        "seed": "67575cae-70f7-4007-8049-2af56915fcaa",
        "userChannelType": "PC"
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }
    try:
        res = session.post(url, json=payload, headers=headers)
        if res.status_code == 200:
            data = res.json().get("result", {})
            return data.get("list", []), data.get("totalCount", 0)
    except Exception as e:
        print("Fetch error:", e)
    return [], 0

direction_map = {
    "SS": "남향", "NN": "북향", "EE": "동향", "WW": "서향",
    "WS": "남서향", "ES": "남동향", "EN": "북동향", "WN": "북서향"
}

def run_v2_scraper():
    print("==================================================")
    print("[RealFifty V3] Next.js API Scraper (50 Complexes)")
    print("==================================================")
    
    session = requests.Session(impersonate="chrome110")
    
    mapping_path = os.path.join(current_dir, "naver_complex_mapping.json")
    with open(mapping_path, "r", encoding="utf-8") as f:
        naver_mapping = json.load(f)
        
    complexes_db = supabase.table("complexes").select("*").execute().data
    all_results = []
    
    for c_meta in complexes_db:
        complex_no_db = str(c_meta["complex_no"])
        apt_name = c_meta["name"].encode('cp949','replace').decode('cp949')
        
        nid_list = naver_mapping.get(complex_no_db)
        if not nid_list: continue
        if isinstance(nid_list, str): nid_list = [nid_list]
        
        for nid in nid_list:
            print(f"\\n👉 [{apt_name}] 데이터 스캔 (ID: {nid}) ...")
            
            info_res = session.get(f'https://fin.land.naver.com/front-api/v1/complex/pyeongList?complexNumber={nid}')
            if info_res.status_code != 200: continue
            
            pyeongs = info_res.json().get('result', [])
            
            for ptp in pyeongs:
                ptp_no = str(ptp.get('number'))
                ptp_nm = ptp.get('name')
                ex_area = float(ptp.get('exclusiveArea', 0) or 0)
                sup_area = float(ptp.get('supplyArea', 0) or 0)
                
                sale_articles_wrapper, sale_count = fetch_top_listings(session, nid, ptp_no, "A1")
                sale_articles = [art.get("representativeArticleInfo", {}) for art in sale_articles_wrapper]
                
                lowest_ask = 0
                normal_lowest_ask = 0
                top_5_json = []
                
                for info in sale_articles[:5]:
                    priceInfo = info.get("priceInfo", {})
                    price = priceInfo.get("dealPrice", 0)
                    
                    floor_str = info.get("articleDetail", {}).get("floorInfo", info.get("floorInfo", ""))
                    is_low_floor = "1/" in floor_str or "저/" in floor_str or "지" in floor_str
                    
                    dir_code = info.get("articleDetail", {}).get("direction", info.get("direction", ""))
                    direction = direction_map.get(dir_code, dir_code)
                    
                    if price > 0:
                        eok = price // 100000000
                        man = (price % 100000000) // 10000
                        price_str = f"{eok}억 {man:,}" if man > 0 else f"{eok}억"
                    else:
                        price_str = "0"
                    
                    top_5_json.append({
                        "price": price,
                        "price_str": price_str,
                        "floor": floor_str,
                        "direction": direction,
                        "realtor": info.get("brokerInfo", {}).get("brokerageName", info.get("realtorName", "")),
                        "tel": "",
                        "mobile": "",
                        "desc": info.get("articleDetail", {}).get("articleFeatureDescription", info.get("articleFeatureDescription", "")),
                        "date": info.get("articleConfirmDate", "").replace("-", "")
                    })
                    
                    if lowest_ask == 0: lowest_ask = price
                    if normal_lowest_ask == 0 and not is_low_floor: normal_lowest_ask = price
                    
                if normal_lowest_ask == 0: normal_lowest_ask = lowest_ask
                
                jeonse_articles_wrapper, jeonse_count = fetch_top_listings(session, nid, ptp_no, "B1")
                if jeonse_articles_wrapper:
                    first_info = jeonse_articles_wrapper[0].get("representativeArticleInfo", {})
                    jeonse_lowest = first_info.get("priceInfo", {}).get("warrantyPrice", 0)
                else:
                    jeonse_lowest = 0
                
                jeonse_rate = round((jeonse_lowest / normal_lowest_ask * 100), 1) if normal_lowest_ask > 0 and jeonse_lowest > 0 else 0
                
                print(f"  👉 평형 {ptp_nm:<4} | 매매 {sale_count}개 | 최저 {normal_lowest_ask//10000}만 | 전세 {jeonse_count}개 ({jeonse_rate}%)")
                
                all_results.append({
                    "crawled_date": today_str,
                    "complex_no": complex_no_db,
                    "naver_complex_no": nid,
                    "complex_name": apt_name,
                    "ptp_name": ptp_nm,
                    "ptp_no": ptp_no,
                    "exclusive_area": ex_area,
                    "supply_area": sup_area,
                    
                    "lowest_ask": lowest_ask,
                    "normal_lowest_ask": normal_lowest_ask,
                    "sale_count": sale_count,
                    "jeonse_count": jeonse_count,
                    "jeonse_lowest_ask": jeonse_lowest,
                    "jeonse_rate": jeonse_rate,
                    "top_5": top_5_json
                })
                
            time.sleep(random.uniform(0.1, 0.4))
            
    out_path = os.path.join(current_dir, f"raw_daily_asks_{today_str}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
        
    print(f"\\n[SUCCESS] 모든 수집 완료! 총 {len(all_results)}개 평형 데이터가 저장되었습니다: {out_path}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_v2_scraper()
