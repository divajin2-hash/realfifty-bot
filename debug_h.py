import os, sys, requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
molit_key = unquote(os.environ.get('RTMS_API_KEY'))

for ym in ['202601', '202605']:
    r = requests.get('http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev', params={'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': ym, 'numOfRows': 1000})
    root = ET.fromstring(r.content)
    for item in root.findall('.//item'):
        if '현대1차' in item.findtext('aptNm'):
            price = int(item.findtext('dealAmount').replace(',', '')) * 10000
            area = float(item.findtext('excluUseAr'))
            dy = f"{ym[:4]}-{int(ym[4:]):02d}-{int(item.findtext('dealDay')):02d}"
            
            try:
                sb.table('rtms_transactions').insert({
                    'complex_id': '94379391-ef97-4ce2-a4a1-bcb00a070ba7',
                    'deal_price': price,
                    'match_key_area': int(round(area)),
                    'exclusive_area_exact': area,
                    'deal_date': dy,
                    'floor': int(item.findtext('floor')),
                    'transaction_type': item.findtext('reqGbn')
                }).execute()
                print(f'Inserted {dy} {price}')
            except Exception as e:
                print(f'Error inserting {dy} {price}:', e)
