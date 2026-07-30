import os, sys, xml.etree.ElementTree as ET, requests
from urllib.parse import unquote
from supabase import create_client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

c_id = supabase.table('complexes').select('id').eq('complex_no', '890').execute().data[0]['id']
key = unquote(os.environ['RTMS_API_KEY'])

url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
all_deals = []

for y in range(2014, 2027):
    for m in range(1, 13):
        if y == 2026 and m > 7: break
        ym = f'{y}{m:02d}'
        try:
            r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11710', 'DEAL_YMD': ym, 'numOfRows': 3000}, timeout=8)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                apt = item.findtext('aptNm', '')
                if '주공' not in apt or '5' not in apt: continue
                if '직거래' in item.findtext('dealingGbn', ''): continue
                if '잠실동' not in item.findtext('umdNm', ''): continue
                pr = int(item.findtext('dealAmount').replace(',','').strip()) * 10000
                ar = float(item.findtext('excluUseAr'))
                d = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
                f = int(item.findtext('floor'))
                all_deals.append({
                    'complex_id': c_id, 'match_key_area': int(round(ar)),
                    'deal_date': d, 'deal_price': pr, 'floor': f,
                    'exclusive_area_exact': ar,
                    'transaction_type': item.findtext('dealingGbn', '')
                })
        except: pass

print(f"총 {len(all_deals)}건 수집 완료. DB 삽입 시작...")

# Insert one by one to avoid any chunk issue
success = 0
for row in all_deals:
    try:
        supabase.table('rtms_transactions').insert(row).execute()
        success += 1
    except: pass  # duplicate skip

print(f"✅ 잠실주공5단지 {success}건 삽입 성공!")

# Verify
tx = supabase.table('rtms_transactions').select('id', count='exact').eq('complex_id', c_id).execute()
print(f"DB 총 건수: {tx.count}")
