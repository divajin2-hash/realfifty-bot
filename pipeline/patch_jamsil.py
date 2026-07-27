import os, sys, xml.etree.ElementTree as ET, requests
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# get jamsil 5 ID
c_id = supabase.table('complexes').select('id, name').eq('complex_no', '890').execute().data[0]['id']

key = unquote(os.environ['RTMS_API_KEY'])
def get_jam_deals():
    valid = []
    for y in range(2014, 2027):
        for m in range(1, 13):
            if y == 2026 and m > 7: break
            ym = f'{y}{m:02d}'
            url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
            try:
                r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11710', 'DEAL_YMD': ym, 'numOfRows': 3000}, timeout=5)
                root = ET.fromstring(r.content)
                for item in root.findall('.//item'):
                    apt = item.findtext('aptNm', '')
                    if '주공' in apt and '5' in apt:
                        if '직거래' in item.findtext('dealingGbn', ''): continue
                        if '잠실동' not in item.findtext('umdNm', ''): continue
                        pr = int(item.findtext('dealAmount').replace(',','').strip()) * 10000
                        ar = float(item.findtext('excluUseAr'))
                        d = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
                        f = int(item.findtext('floor'))
                        valid.append({'complex_id': c_id, 'match_key_area': int(round(ar)), 'deal_date': d, 'deal_price': pr, 'floor': f, 'exclusive_area_exact': ar, 'transaction_type': item.findtext('dealingGbn', '')})
            except Exception as e: pass
            print(f'Fetched {ym}')
    return valid

deals = get_jam_deals()
print(f'\nFound {len(deals)} deals for Jamsil 5')

if deals:
    for i in range(0, len(deals), 500):
        try:
            supabase.table('rtms_transactions').upsert(deals[i:i+500], on_conflict='complex_id,match_key_area,deal_date,deal_price,floor').execute()
        except Exception as e: print(e)
print('Done!')
