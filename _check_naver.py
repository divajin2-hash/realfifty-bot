import os
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
sb = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
res = sb.table('complexes').select('id, name, naver_id').eq('name', '래미안슈르').execute()
nid = res.data[0]['naver_id']

url = f'https://new.land.naver.com/api/complexes/{nid}'
headers = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=headers).json()

print("네이버 PTP:")
for ptp in r.get('complexPyeongDetailList', []):
    if 80 < ptp['exclusiveArea'] < 90:
        print(f"{ptp['pyeongName']} -> 전용면적: {ptp['exclusiveArea']}")
