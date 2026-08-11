import os, json
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
c_no = supabase.table('complexes').select('complex_no').ilike('name', '%슈르%').execute().data[0]['complex_no']
asks = json.load(open('pipeline/raw_daily_asks_2026-08-07.json', encoding='utf-8'))
for x in asks:
    if str(x['complex_no']) == str(c_no):
        if '108' in x['ptp_name'] or '109' in x['ptp_name'] or '110' in x['ptp_name']:
            print(f"{x['ptp_name']}: {x['exclusive_area']}")
