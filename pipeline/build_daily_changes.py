"""Publish type-level ask changes from raw daily collections; never infer new trades from prices."""
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
ROOT=Path(__file__).resolve().parents[1]

def build(groups, current, previous, date, previous_date):
    def index(rows):
        result={}
        for r in rows:
            key=(str(r.get('naver_complex_no')),str(r.get('ptp_no')))
            if key in result: raise ValueError('Duplicate source type')
            result[key]=r
        return result
    if any(r.get("crawled_date", date) != date for r in current) or any(r.get("crawled_date", previous_date) != previous_date for r in previous):
        raise ValueError("Source collection dates do not match")
    cur,prev=index(current),index(previous)
    rows=[]; comparable=0; unchanged=0; appeared=0; disappeared=0; missing=0
    for g in groups:
        for s in g['stats']:
            key=(str(s.get('naver_complex_no')),str(s.get('naver_ptp_no')))
            a,b=cur.get(key),prev.get(key)
            if not a or not b or a.get('exclusive_area') != b.get('exclusive_area'):
                missing+=1;continue
            x,y=a.get('lowest_ask'),b.get('lowest_ask')
            if not isinstance(x,(int,float)) or not isinstance(y,(int,float)):
                missing+=1;continue
            if x<=0 or y<=0:
                # Absence is a separate state, never a 100% price movement.
                appeared+=int(x>0 and y<=0);disappeared+=int(y>0 and x<=0);continue
            comparable+=1
            if x==y: unchanged+=1;continue
            area=f"{s.get('naver_ptp_no') or ''}:{s.get('pyeong_name') or ''}:{s.get('exclusive_area') or s['match_key_area']:g}"
            rows.append(dict(id=g['complex']['id'],name=g['complex']['name'],area=area,label=f"{s.get('pyeong_name','')} · 전용 {s.get('exclusive_area')}㎡",before=y,after=x,percent=(x/y-1)*100))
    return dict(date=date,previousDate=previous_date,generatedAt=groups[0]['generated_at'],comparable=comparable,unchanged=unchanged,appeared=appeared,disappeared=disappeared,missing=missing,rises=sum(r['after']>r['before'] for r in rows),falls=sum(r['after']<r['before'] for r in rows),rows=sorted(rows,key=lambda r:(r['name'],r['area'])),tradeStatus='unavailable')

def run():
    groups=json.loads((ROOT/'web/src/data/kb50_stats.json').read_text(encoding='utf-8'))
    date=datetime.fromisoformat(groups[0]['generated_at']).astimezone(timezone(timedelta(hours=9))).date().isoformat()
    files=sorted((ROOT/'pipeline').glob('raw_daily_asks_*.json'))
    current=ROOT/'pipeline'/f'raw_daily_asks_{date}.json'
    prior=[p for p in files if p.stem[-10:]<date]
    target=ROOT/'web/src/data/daily_changes.json'
    if not current.exists() or not prior:
        result={'date':date,'generatedAt':groups[0]['generated_at'],'unavailable':True}
    else:
        previous=prior[-1]
        result=build(groups,json.loads(current.read_text(encoding='utf-8')),json.loads(previous.read_text(encoding='utf-8')),date,previous.stem[-10:])
    temp=target.with_suffix('.tmp');temp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(target)
    print('Daily changes:',result.get('comparable',0),'comparable types;',len(result.get('rows',[])),'changed')
if __name__=='__main__':run()
