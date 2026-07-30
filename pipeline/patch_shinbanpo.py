import requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
key = unquote(os.environ['RTMS_API_KEY'])
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

cid = supabase.table('complexes').select('id').eq('complex_no', '1275').execute().data[0]['id']

# 기존 잘못된(다른 차수 섞인) 데이터 삭제
supabase.table('rtms_transactions').delete().eq('complex_id', cid).execute()
print("기존 데이터 삭제 완료")

url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
all_deals = []

for y in range(2014, 2027):
    for m in range(1, 13):
        if y == 2026 and m > 7: break
        ym = f'{y}{m:02d}'
        try:
            r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11650', 'DEAL_YMD': ym, 'numOfRows': 3000}, timeout=8)
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                apt = item.findtext('aptNm', '')
                umd = item.findtext('umdNm', '')
                
                # 정확히 '신반포2'만 허용 ('신반포22', '신반포27' 등 배제)
                apt_clean = apt.replace('(', '').replace(')', '').replace(' ', '').strip()
                if apt_clean != '신반포2' and apt_clean != '신반포2차' and apt_clean != '한신2차': continue
                
                if '직거래' in item.findtext('dealingGbn', ''): continue
                pr = int(item.findtext('dealAmount').replace(',','').strip()) * 10000
                ar = float(item.findtext('excluUseAr'))
                d = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
                f = int(item.findtext('floor'))
                all_deals.append({
                    'complex_id': cid, 'match_key_area': int(round(ar)),
                    'deal_date': d, 'deal_price': pr, 'floor': f,
                    'exclusive_area_exact': ar,
                    'transaction_type': item.findtext('dealingGbn', ''),
                    '_apt': apt, '_umd': umd
                })
        except: pass

print(f"\n정밀 수집 완료: {len(all_deals)}건")
areas = {}
for d in all_deals:
    ea = d['exclusive_area_exact']
    if ea not in areas: areas[ea] = 0
    areas[ea] += 1
    
print("면적 분포:")
for ea, cnt in sorted(areas.items()):
    print(f"  {ea}㎡ (match_key={int(round(ea))}) → {cnt}건")

# 이름 확인
names = set(d['_apt'] for d in all_deals)
print(f"\n수집된 아파트명: {names}")

# Insert
success = 0
for row in all_deals:
    del row['_apt']
    del row['_umd']
    try:
        supabase.table('rtms_transactions').insert(row).execute()
        success += 1
    except: pass

print(f"\n✅ {success}건 삽입 성공!")
