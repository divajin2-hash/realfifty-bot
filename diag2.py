import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv('pipeline/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

r = supabase.table('pyeong_stats').select('complex_id, match_key_area, current_lowest_ask, is_mocked_price, complexes(name)').eq('is_mocked_price', True).execute()
for d in r.data:
    print(f"[{d['complexes']['name']}] {d['match_key_area']} -> {d['current_lowest_ask']}")
print(f"Total Fallbacks: {len(r.data)}")
