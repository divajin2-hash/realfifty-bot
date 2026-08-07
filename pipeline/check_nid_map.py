import json, os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))
complexes = supabase.table('complexes').select('id, name, complex_no').execute().data

with open('pipeline/naver_complex_mapping.json', 'r', encoding='utf-8') as f:
    nmap = json.load(f)

for c in complexes:
    cno = str(c['complex_no'])
    if cno in nmap:
        print(f"{c['name']}: cno={cno} -> nids={nmap[cno]}")
