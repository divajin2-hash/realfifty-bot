"""Pure refresh planning; dates are supplied in Korea Standard Time."""
from datetime import date

def plan_refresh(now, complexes, groups, full=False):
    months=[f'{y:04d}{m:02d}' for y in range(2014,now.year+1) for m in range(1,13) if (y,m)<=(now.year,now.month)]
    monthly=now.weekday()==6 and now.day<=7
    mode='full' if full or monthly else 'weekly' if now.weekday()==6 else 'daily'
    selected=months if mode=='full' else months[-(12 if mode=='weekly' else 3):]
    codes={str(c['id']):c['bjd_code'][:5] for c in complexes}
    pairs={(code,month) for code in codes.values() for month in selected}
    for g in groups:
        code=codes.get(str(g['complex']['id']))
        if not code:raise ValueError('Displayed complex missing from official inventory')
        for s in g['stats']:
            for stamp in [(s.get('recent_deal_absolute') or {}).get('date'),s.get('highest_deal_date')]:
                if not stamp:continue
                parsed=date.fromisoformat(stamp)
                if parsed>now or parsed.year<2014:raise ValueError('Displayed reference date outside verified scope')
                pairs.add((code,parsed.strftime('%Y%m')))
    return mode,pairs
