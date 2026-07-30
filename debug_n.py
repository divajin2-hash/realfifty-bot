import json
with open('pipeline/raw_daily_asks_2026-07-28.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
for node in d:
    if node.get('complex_name') == '현대(1~5차)':
        print(f"{node['ptp_name']} -> Naver Exclusive: {node['exclusive_area']}, Asks: {len(node.get('asks', []))}")
