import json
with open('web/src/data/kb50_stats.json', encoding='utf-8') as f:
    data = json.load(f)

for c in data:
    if '리센츠' in c['complex']['name'] or '디에이치퍼스티어' in c['complex']['name'] or '개포자이' in c['complex']['name']:
        print(f"--- {c['complex']['name']} ---")
        for s in c['stats']:
            if s.get('match_key_area') in [84, 85]:
                print(f"{s['pyeong_name']}: total {len(s.get('all_trades_history', []))} trades. Max: {s.get('highest_deal_price')}, Recent: {s.get('recent_deal_absolute')}")
