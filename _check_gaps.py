import json

data = json.load(open('web/src/data/kb50_stats.json', encoding='utf-8'))
gaps = []
for c in data:
    for s in c['stats']:
        rd = s.get('recent_deal_absolute')
        ask = s.get('current_lowest_ask')
        if rd and ask and rd.get('price') > 0 and ask > 0:
            gap = ((ask - rd['price']) / rd['price']) * 100
            if gap > 5:
                gaps.append((gap, c['complex']['name'], s.get('pyeong_name'), ask//100000000, rd['price']//100000000, rd.get('date')))

gaps.sort(reverse=True, key=lambda x: x[0])
for g in gaps[:10]:
    print(f"{g[1]} {g[2]} : Gap {g[0]:.1f}% (Ask {g[3]} vs Deal {g[4]} Date: {g[5]})")
