import os, json
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone

load_dotenv('pipeline/.env')
supabase = create_client(os.environ['SUPABASE_URL'], os.environ['SUPABASE_KEY'])

def format_price(price):
    eok = price // 100000000
    man = (price % 100000000) // 10000
    res = ""
    if eok > 0:
        res += f"{eok}억"
    if man > 0:
        res += f" {man}만" if eok > 0 else f"{man}만"
    return res

KST = timezone(timedelta(hours=9))
today_date = datetime.now(KST).strftime('%Y-%m-%d')

res_today = supabase.table('daily_history').select('*').eq('base_date', today_date).execute()
res_yest_q = supabase.table('daily_history').select('base_date').lt('base_date', today_date).order('base_date', desc=True).limit(1).execute()
prev_date = res_yest_q.data[0]['base_date'] if res_yest_q.data else '2026-08-05'
res_yest = supabase.table('daily_history').select('*').eq('base_date', prev_date).execute()

yest_dict = {(r['complex_id'], r['area']): r for r in res_yest.data}

# Load pyeong_name map
pyeong_name_map = {}
kb50 = json.load(open('web/src/data/kb50_stats.json', encoding='utf-8'))
for cx in kb50:
    cx_id = cx['complex'].get('id')
    for s in cx.get('stats', []):
        area = s.get('match_key_area')
        pname = s.get('pyeong_name')
        if cx_id and area and pname:
            pyeong_name_map[(cx_id, area)] = pname

print(f"pyeong_name_map: {len(pyeong_name_map)} entries")
print(f"Comparing {today_date} vs {prev_date}")
print()

ask_changes = []
for t in res_today.data:
    key = (t['complex_id'], t['area'])
    y = yest_dict.get(key)
    if not y:
        continue
    t_ask = t.get('lowest_ask') or 0
    y_ask = y.get('lowest_ask') or 0
    if t_ask > 0 and y_ask > 0 and t_ask != y_ask:
        c_name = t['complex_name']
        area = t['area']
        diff = t_ask - y_ask
        mark = "📈상승" if diff > 0 else "📉하락"
        line = f"- {c_name} {area}㎡: {format_price(y_ask)} -> {format_price(t_ask)} ({mark} {format_price(abs(diff))})"
        pname = pyeong_name_map.get((t.get('complex_id'), area))
        if pname and pname != str(area):
            line = line.replace(f"{c_name} {area}㎡:", f"{c_name} {pname}({area}㎡):")
        ask_changes.append(line)

print(f"ask_changes: {len(ask_changes)}건")
for line in ask_changes[:10]:
    print(line)
