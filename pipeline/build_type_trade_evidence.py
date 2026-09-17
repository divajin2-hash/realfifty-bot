"""Build transaction-specific evidence, never a nearest-area rule. No DB writes."""
import argparse,json
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone
from decimal import Decimal
from type_matching import trade_key,area_key

def resolve_area(raw_areas, asking_area, anchors):
    exact=Decimal(str(asking_area))
    if exact in raw_areas:
        return exact,'exact_original_area'
    supported=raw_areas.intersection(anchors)
    if len(supported)==1:
        return next(iter(supported)),'independent_trade_area'
    return None,None

def build(asks,verified,cache):
    names={c['name']:c['id'] for c in verified['complexes']}
    index=defaultdict(list)
    for t in verified['transactions']:
        index[(t['complex_id'],t['deal_date'],t['deal_price'],t.get('floor'))].append(t)
    types={};unresolved=[];resolved_multiple=[]
    for a in asks:
        key=f"{a['naver_complex_no']}:{a['ptp_no']}"
        path=cache/f"{a['naver_complex_no']}-{a['ptp_no']}.json"
        if not path.exists():raise ValueError(f'Missing source cache: {key}')
        accepted=set();pending=[];anchors=defaultdict(set)
        for r in json.loads(path.read_text(encoding='utf-8'))['rows']:
            if r.get('isDelete') or '직거래' in r.get('tradeCategory','') or r['tradeDate']<'2014-01-01':continue
            candidates=index.get((names.get(a['complex_name']),r['tradeDate'],r['dealPrice'],r.get('floor')),[])
            source='molit_apt' if r.get('propertyType')=='NORMAL' else 'molit_rights' if r.get('propertyType') in ('PRESALE','OCCUPANCY_RIGHT') else None
            candidates=[t for t in candidates if source is not None and t.get('source')==source]
            raw_areas={Decimal(str(t['exclusive_area_exact'])) for t in candidates}
            if len(raw_areas)==1:
                accepted.update(trade_key(t) for t in candidates)
                anchors[source].update(raw_areas)
            elif raw_areas:
                pending.append((r,source,candidates,raw_areas))
            else:
                unresolved.append({'complex':a['complex_name'],'type_key':key,'date':r['tradeDate'],'price':r['dealPrice'],'floor':r.get('floor'),'reason':'multiple_original_areas' if raw_areas else 'no_source_match','candidate_areas':sorted(map(str,raw_areas))})
        # Second pass: only independent unambiguous rows seed the source-specific anchors.
        # Resolved ambiguous rows never seed other resolutions (no circular inference).
        for r,source,candidates,raw_areas in pending:
            selected,method=resolve_area(raw_areas,a['exclusive_area'],anchors[source])
            detail={'complex':a['complex_name'],'type_key':key,'date':r['tradeDate'],'price':r['dealPrice'],'floor':r.get('floor'),'candidate_areas':sorted(map(str,raw_areas))}
            if selected is None:
                unresolved.append({**detail,'reason':'multiple_original_areas'})
            else:
                accepted.update(trade_key(t) for t in candidates if Decimal(str(t['exclusive_area_exact']))==selected)
                resolved_multiple.append({**detail,'selected_area':str(selected),'method':method,'source':source})
        types[key]={'complex_id':names.get(a['complex_name']),'asking_area':a['exclusive_area'],'trade_keys':sorted(accepted)}
    return {'version':2,'generated_at':datetime.now(timezone.utc).isoformat(),'policy':'same transaction signature and source; multiple areas resolved by exact raw area or independent unique-area anchors; transaction-specific only','types':types,'unresolved':unresolved,'resolved_multiple':resolved_multiple}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--asks',type=Path,required=True);args=p.parse_args()
    root=Path(__file__).parent
    result=build(json.loads(args.asks.read_text(encoding='utf-8')),json.loads((root/'rtms_recheck/verified_full.json').read_text(encoding='utf-8')),args.cache)
    (root/'type_trade_evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Types',len(result['types']),'unresolved display rows',len(result['unresolved']))
