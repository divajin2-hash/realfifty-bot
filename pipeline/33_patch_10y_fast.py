import os, time, requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run():
    complexes = supabase.table("complexes").select("*").execute().data
    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
    safe_key = unquote(os.environ['RTMS_API_KEY'])
    
    # Generate YMD tasks
    months = [f"{y}{m:02d}" for y in range(2014, 2027) for m in range(1, 13)]
    months = [m for m in months if not (m.startswith('2026') and int(m[-2:]) > 8)]

    for lawd, apts in lawd_map.items():
        print(f"\nProcessing {lawd} ...")
        for ymd in months:
            try:
                res = requests.get(url, params={'serviceKey': safe_key, 'LAWD_CD': lawd, 'DEAL_YMD': ymd, 'numOfRows': 9999}, timeout=10)
                if res.status_code != 200: continue
                root = ET.fromstring(res.content)
                trades = []
                for item in root.findall('.//item'):
                    item_apt = item.findtext('aptNm')
                    if not item_apt: continue
                    api_name = item_apt.replace("(", "").replace(")", "").replace(" ", "")
                    matched_c = None
                    for c in apts:
                        db_name = c['name'].split('(')[0].replace(" ", "")
                        if db_name in api_name or api_name in db_name:
                            matched_c = c
                            break
                    if not matched_c: continue
                    # Ignore old One Bailey
                    if '원베일리' in matched_c['name'] and ymd < '202308': continue

                    price = format_price(item.findtext("dealAmount"))
                    area_exact = float(item.findtext("excluUseAr"))
                    mk = int(round(area_exact))
                    if matched_c["id"] == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(area_exact - 82.23) < 0.01: mk = 83
                    
                    d_str = f"{ymd[:4]}-{int(ymd[4:]):02d}-{int(item.findtext('dealDay')):02d}"
                    trades.append({
                        "complex_id": matched_c["id"],
                        "match_key_area": mk,
                        "deal_date": d_str,
                        "deal_price": price,
                        "floor": int(item.findtext("floor", "0")),
                        "exclusive_area_exact": area_exact,
                        "transaction_type": item.findtext("dealingGbn", " ")
                    })
                    
                if trades:
                    supabase.table("rtms_transactions").upsert(trades, on_conflict="complex_id, match_key_area, deal_date, deal_price, floor").execute()
            except Exception as e:
                pass
            time.sleep(0.01)

if __name__ == '__main__':
    run()
