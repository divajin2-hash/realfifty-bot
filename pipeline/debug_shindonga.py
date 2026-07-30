import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# 1. 신동아 DB 데이터 확인
res = supabase.table('complexes').select('*').execute()
for c in res.data:
    if '신동아' in c['name']:
        print(f"Complex: {c['name']} | ID: {c['id']} | No: {c['complex_no']}")
        cid = c['id']

        ps = supabase.table('pyeong_stats').select('*').eq('complex_id', cid).execute()
        for p in ps.data:
            ask = p['current_lowest_ask']
            ath = p['highest_deal_price']
            mdd = p['mdd_rate']
            print(f"  평형 {p['match_key_area']}㎡ | 최저호가: {ask:,} | 최고가: {ath:,} | MDD: {mdd}%")

        tx = supabase.table('rtms_transactions').select('match_key_area, deal_price, deal_date').eq('complex_id', cid).order('deal_price', desc=True).limit(10).execute()
        print('  Top 10 거래:')
        for t in tx.data:
            print(f"    {t['match_key_area']}㎡ | {t['deal_price']:,} | {t['deal_date']}")

# 2. 네이버 원시 데이터에서 신동아 확인
with open('d:/appmaking/kb50_mdd/pipeline/raw_daily_asks_2026-07-27.json', 'r', encoding='utf-8') as f:
    asks = json.load(f)

for c in res.data:
    if '신동아' in c['name']:
        cno = c['complex_no']
        print(f"\n--- 네이버 RAW 데이터 (complex_no={cno}) ---")
        for a in asks:
            if a.get('complex_no') == cno:
                print(f"  {a.get('ptp_name')} | 전용 {a.get('exclusive_area')}㎡ | 최저가: {a.get('lowest_ask'):,}")
