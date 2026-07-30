import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from supabase import create_client
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

# 1. 전체 단지 목록
complexes = supabase.table('complexes').select('*').execute().data
print(f"=== 전체 {len(complexes)}개 단지 진단 ===\n")

# 2. 각 단지별 rtms 건수, pyeong_stats 건수, 네이버 호가 건수 비교
with open('d:/appmaking/kb50_mdd/pipeline/raw_daily_asks_2026-07-27.json', 'r', encoding='utf-8') as f:
    asks = json.load(f)

# Group asks by complex_no
ask_map = {}
for a in asks:
    cno = a.get('complex_no')
    if cno not in ask_map: ask_map[cno] = []
    ask_map[cno].append(a)

problems = []

for c in sorted(complexes, key=lambda x: x['name']):
    cid = c['id']
    cno = c['complex_no']
    name = c['name']
    
    # rtms count
    tx = supabase.table('rtms_transactions').select('id', count='exact').eq('complex_id', cid).execute()
    tx_count = tx.count or 0
    
    # pyeong_stats count
    ps = supabase.table('pyeong_stats').select('id', count='exact').eq('complex_id', cid).execute()
    ps_count = ps.count or 0
    
    # naver asks count
    naver_count = len(ask_map.get(cno, []))
    
    status = "✅"
    issue = ""
    if tx_count == 0:
        status = "❌"
        issue = "국토부 거래 0건!"
        problems.append((name, cno, 'NO_RTMS'))
    elif ps_count == 0 and naver_count > 0:
        status = "⚠️"
        issue = "호가 있으나 MDD 미매칭"
        problems.append((name, cno, 'NO_MDD'))
    elif naver_count == 0:
        status = "⚠️"
        issue = "네이버 호가 수집 실패"
        problems.append((name, cno, 'NO_NAVER'))
    
    print(f"{status} {name:20s} | 국토부: {tx_count:5d}건 | MDD: {ps_count:2d}개 | 네이버: {naver_count:2d}개 {issue}")

print(f"\n\n=== 문제 단지 요약 ===")
for name, cno, kind in problems:
    print(f"  ❌ {name} (No.{cno}) → {kind}")
