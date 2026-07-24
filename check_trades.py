import json
with open('web/src/data/kb50_stats.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for g in data:
    if '래미안슈르' in g['complex']['name']:
        for s in g['stats']:
            if s['match_key_area'] == 59:
                for t in s['month_deals']:
                    print(t)
                print("Total month deals for 59:", len(s['month_deals']))
