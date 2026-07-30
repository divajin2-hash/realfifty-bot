import os
from dotenv import load_dotenv
from supabase import create_client
import sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])
data = supabase.table('complexes').select('*').execute().data

print('| 국토부/DB번호(complex_no) | 주소(region) | 단지명(name) | 네이버 고유번호(complexNo) (비워둠) |')
print('|:---:|:---|:---|:---|')
for d in data:
    print(f'| {d["complex_no"]} | {d["region"]} | {d["name"]} | |')
