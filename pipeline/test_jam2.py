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
url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11710', 'DEAL_YMD': '202105', 'numOfRows': 3000}, timeout=5)
root = ET.fromstring(r.content)

valid = []
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

print(f"Upserting {len(valid)} rows...")
try:
    res = supabase.table('rtms_transactions').upsert(valid, on_conflict='unique_rtms_deal').execute()
    print("SUCCESS UPSERT:", len(res.data))
except Exception as e:
    print("FAILED UPSERT:", e)
    # try one by one safely
    for row in valid:
        try:
            supabase.table('rtms_transactions').insert(row).execute()
        except: pass
    
tx = supabase.table('rtms_transactions').select('id', count='exact').eq('complex_id', c_id).execute()
print("Total Jam5 deals now:", tx.count)
