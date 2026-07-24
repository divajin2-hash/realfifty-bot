import json

with open('web/src/data/kb50_stats.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for c in db:
    name = c['complex']['name']
    for p in c['stats']:
        ath = p.get('highest_deal_price', 0)
        recent_deal = p.get('recent_deal_absolute')
        recent = recent_deal.get('price', 0) if recent_deal else 0
        recent_date = recent_deal.get('date', '') if recent_deal else ''
        area = p['match_key_area']
        date = p.get('highest_deal_date', '')
        
        # Criteria 1: Suspiciously low ATH for >= 84m2 (Less than 700m KRW in Top 50 is impossible except maybe very fast canceled deals or totally weird data)
        # Check Top 50, even Suwon/Seongnam > 700m for 84m2.
        if area >= 84 and ath < 700000000:
            print(f"[LOW_ATH] {name.encode('unicode_escape').decode()} | {area} | {ath//10000}만 | {date}")
            
        # Criteria 2: Dead Ghost reconstruction aliases
        # If ATH was before 2021 and there is zero action since 2022.
        if date.startswith('201') or date.startswith('2020'):
            if not recent_date or recent_date < '2022-01-01':
                print(f"[GHOST] {name.encode('unicode_escape').decode()} | {area}m2 | ATH {date} | RECENT {recent_date}")
