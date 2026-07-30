import json
data = json.load(open('web/src/data/kb50_stats.json', encoding='utf-8'))
fallbacks = []
for c in data:
    for p in c['stats']:
        if p.get('is_mocked_price', False):
            fallbacks.append(f"[{c['complex']['name']}] {p['match_key_area']} -> {p['current_lowest_ask']} (Fallback)")
for f in fallbacks: print(f)
print(f'Total fallbacks: {len(fallbacks)}')
