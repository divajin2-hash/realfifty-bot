import json

with open('web/src/data/kb50_stats.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

for c in db:
    name = c['complex']['name']
    for p in c['stats']:
        ath = p.get('highest_deal_price', 0)
        recent = p.get('recent_deal_absolute', {}).get('price', 0)
        area = p['match_key_area']
        date = p.get('highest_deal_date', '')
        
        # In Seoul/Gyeonggi TOP 50, properties >= 59m2 shouldn't generally have an ATH under 5억 (500M KRW).
        # Also, if area is unusually large and ath is unusually small:
        if area >= 84 and ath < 700000000: # 7억
            print(f"[SUSPICIOUS ATH TOO LOW] {name} Area {area}m2: ATH {ath//10000}만 ({date})")
        
        # Also, check if there's an area under 40m2 which typically belong to old reconstructions or officetels mixing in.
        # But some mega-complexes actually have studio types (like Helio City 39m2, Parkrio 35m2).
        if area < 40 and not any(k in name for k in ['헬리오시티', '파크리오', '은마', '주공', '현대', '시영', '래미안센트럴스위트']): 
            print(f"[SUSPICIOUS TINY AREA] {name} Area {area}m2")
            
        # Also flag complexes where ATH occurred BEFORE 2021 AND there are zero recent deals
        # This usually means it's a dead reconstructed ghost complex record.
        recent_date = p.get('recent_deal_absolute', {}).get('date', '')
        if date.startswith('201') or date.startswith('2020'):
            # If there's absolutely no deal in the last 3 years:
            if not recent_date or recent_date < "2023-01-01":
                print(f"[SUSPICIOUS DEAD GHOST] {name} Area {area}m2 - ATH in {date}, Recent in {recent_date} (Price: {recent//10000}만)")
             
