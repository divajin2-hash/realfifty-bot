import os, json
from supabase import create_client
from dotenv import load_dotenv
load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

res3 = supabase.table('rtms_transactions').select('complex_id, deal_date').gte('deal_date', '2026-08-01').execute()
print(f'2026-08 거래건수 (국토부 API): {len(res3.data)}건')
unique_complexes = set(r['complex_id'] for r in res3.data)
print(f'이번달 거래 있는 단지 수: {len(unique_complexes)}개')

data = json.load(open('web/src/data/macro_volume_index.json', encoding='utf-8'))
print(f'\nATH month: {data["ath_month"]} ({data["ath_count"]}건)')
for m in data['timeline'][-5:]:
    print(f'  {m["month"]}: {m["trade_count"]}건 ({m["volume_ratio"]}%)')
