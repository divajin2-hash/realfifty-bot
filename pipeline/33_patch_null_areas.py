import os
import time
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def run():
    print("Fetching missing exclusive areas...")
    # Get all trades where exclusive_area_exact is null
    data = supabase.table('rtms_transactions').select('id, complex_id, deal_date').is_('exclusive_area_exact', 'null').execute().data
    if not data:
        print("No missing areas!")
        return
    
    print(f"Found {len(data)} null trades. Mapping complexes...")
    complexes = supabase.table('complexes').select('*').execute().data
    c_map = {c['id']: c for c in complexes}
    
    # We only need to fetch the months that are missing for specific LAWD_CDs
    tasks = set()
    for t in data:
        c = c_map.get(t['complex_id'])
        if not c: continue
        if '원베일리' in c['name'] and t['deal_date'] < '2023-01-01':
            continue # Skip pre-reconstruction per user
        ymd = t['deal_date'].replace('-', '')[:6]
        lawd = c['bjd_code'][:5]
        tasks.add((lawd, ymd))
        
    print(f"{len(tasks)} unique API tasks to fetch...")
    
    for lawd, ymd in sorted(tasks, key=lambda x: x[1], reverse=True):
        print(f"Fetching {lawd} {ymd}...")
        url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
        params = {'serviceKey': unquote(os.environ['RTMS_API_KEY']), 'LAWD_CD': lawd, 'DEAL_YMD': ymd, 'numOfRows': '5000'}
        try:
            res = requests.get(url, params=params, timeout=20)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                updates = []
                for item in root.findall('.//item'):
                    api_name = item.findtext('aptNm').replace("(", "").replace(")", "").replace(" ", "")
                    area = item.findtext('excluUseAr')
                    if not area: continue
                    price = int(item.findtext('dealAmount').replace(',', '')) * 10000
                    day = int(item.findtext('dealDay'))
                    d_str = f"{ymd[:4]}-{ymd[4:6]}-{day:02d}"
                    updates.append({'api_name': api_name, 'area': float(area), 'price': price, 'date': d_str})
                # Now match against our trades for this LAWD and YMD
                for t in data:
                    if t['deal_date'].replace('-', '')[:6] != ymd: continue
                    c = c_map.get(t['complex_id'])
                    if not c or c['bjd_code'][:5] != lawd: continue
                    db_name = c['name'].replace("(", "").replace(")", "").replace(" ", "")
                    
                    # Find the trade in API
                    for u in updates:
                        if (db_name in u['api_name'] or u['api_name'] in db_name) and u['date'] == t['deal_date']:
                            # It's a match! Are we sure it's the exact same trade? Price matching is best
                            # But since we just need the area, let's update it in DB directly if it matches
                            # Actually, we don't know the exact price of 't' from our query since we didn't fetch it.
                            # To be perfectly safe, we should upsert based on the API data.
                            mk = int(round(u['area']))
                            if c['id'] == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(u['area'] - 82.23) < 0.01: mk = 83
                            
                            supabase.table('rtms_transactions').upsert({
                                "complex_id": c['id'],
                                "match_key_area": mk,
                                "deal_date": u['date'],
                                "deal_price": u['price'],
                                "floor": int(item.findtext("floor", "0")),
                                "exclusive_area_exact": u['area']
                            }, on_conflict="complex_id, match_key_area, deal_date, deal_price, floor").execute()
        except Exception as e: 
            print(f"Err {lawd} {ymd}: {e}")
        time.sleep(0.1)

if __name__ == '__main__':
    run()
