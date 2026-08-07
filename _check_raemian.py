import json
kb50 = json.load(open('web/src/data/kb50_stats.json', encoding='utf-8'))
for cx in kb50:
    if cx['complex']['name'] == '래미안슈르':
        for s in cx['stats']:
            rd = s.get('recent_deal_absolute') or {}
            ask_val = s.get('current_lowest_ask')
            print(f"{s['pyeong_name']}({s['match_key_area']}m2) ask: {ask_val}")
            if rd:
                print(f"  - deal: {rd.get('date')} / {rd.get('price')} / floor:{rd.get('floor')}")
