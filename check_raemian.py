import json
with open('web/src/data/kb50_stats.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for g in data:
    if '래미안슈르' in g['complex']['name']:
        print(g['complex']['name'])
        for s in g['stats']:
            recent = s['recent_deal_absolute']['price'] if s['recent_deal_absolute'] else None
            recent_date = s['recent_deal_absolute']['date'] if s['recent_deal_absolute'] else None
            print(f"  Area: {s['match_key_area']}m2, ATH: {s['highest_deal_price']}, Recent: {recent} ({recent_date})")
