"""Read-only official API backfill. Never updates Supabase."""
import os,json,time,importlib.util,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
from concurrent.futures import ThreadPoolExecutor,as_completed
from urllib.parse import unquote
import requests
import xml.etree.ElementTree as ET
from dotenv import load_dotenv
from supabase import create_client
ROOT=Path(__file__).resolve().parents[1]
load_dotenv(ROOT/'pipeline/.env')
CACHE=ROOT/'pipeline/rtms_recheck'

def collect(code,month,kind='apt',force=False):
    target=CACHE/f'{code}-{month}.json' if kind=='apt' else CACHE/f'rights-{code}-{month}.json'
    refresh_from=os.environ.get('RTMS_REFRESH_FROM','999999')
    if not force and target.exists() and month < refresh_from:return json.loads(target.read_text(encoding='utf-8'))
    rows=[];page=1
    while True:
        root=None
        for attempt in range(3):
            try:
                endpoint='https://apis.data.go.kr/1613000/'+('RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev' if kind=='apt' else 'RTMSDataSvcSilvTrade/getRTMSDataSvcSilvTrade')
                r=requests.get(endpoint,params={'serviceKey':unquote(os.environ['RTMS_API_KEY']),'LAWD_CD':code,'DEAL_YMD':month,'numOfRows':1000,'pageNo':page},timeout=40)
                root=ET.fromstring(r.content)
                if r.status_code!=200 or root.findtext('.//resultCode') not in ('000','00'):raise ValueError('API failed')
                break
            except Exception:
                if attempt==2:raise RuntimeError(f'API failed: {code}/{month}/{page}') from None
                time.sleep(2)
        batch=[{e.tag:(e.text or '').strip() for e in item} for item in root.findall('.//item')]
        rows.extend(batch);total=int(root.findtext('.//totalCount') or 0)
        if len(rows)>=total:break
        if not batch:raise RuntimeError('Incomplete pagination')
        page+=1
    target.write_text(json.dumps(rows,ensure_ascii=False),encoding='utf-8')
    return rows

from complex_matching import name_matches, dong_matches

def main():
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument('--full-refresh',action='store_true')
    args=parser.parse_args()
    CACHE.mkdir(exist_ok=True)
    db=create_client(os.environ['SUPABASE_URL'],os.environ['SUPABASE_KEY'])
    complexes=db.table('complexes').select('*').execute().data
    spec=importlib.util.spec_from_file_location('matcher',ROOT/'pipeline/31_daily_rtms_pro.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    now=datetime.now(timezone(timedelta(hours=9)))
    from rtms_refresh_policy import plan_refresh
    stats_path=ROOT/'web/src/data/kb50_stats.json'
    groups=json.loads(stats_path.read_text(encoding='utf-8')) if stats_path.exists() else []
    refresh_mode,refresh_pairs=plan_refresh(now.date(),complexes,groups,args.full_refresh)
    print(f'Refresh policy: {refresh_mode}; {len(refresh_pairs)} district-month pairs plus missing caches',flush=True)
    months=[f'{year:04d}{month:02d}' for year in range(2014,now.year+1) for month in range(1,13) if (year,month)<=(now.year,now.month)]
    districts=sorted({c['bjd_code'][:5] for c in complexes})
    tasks=[(c,mo,kind) for c in districts for mo in months for kind in ('apt','rights')]
    if not districts:raise RuntimeError('No districts configured')
    allrows=[];done=0;failures=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures={pool.submit(collect,c,mo,kind,(c,mo) in refresh_pairs):(c,mo,kind) for c,mo,kind in tasks}
        for f in as_completed(futures):
            code,mo,kind=futures[f]
            try:
                batch=f.result()
                allrows.extend((code,kind,r) for r in batch)
            except Exception:
                failures.append((code,mo,kind))
                print(f'Failed task: {code}/{mo}/{kind}',flush=True)
            done+=1
            if done%30==0:print(f'Completed {done}/{len(tasks)} district-months',flush=True)
    if failures:
        (CACHE/'failed_tasks.json').write_text(json.dumps(failures),encoding='utf-8')
        raise RuntimeError(f'{len(failures)} source tasks failed; no dataset published. Retry uses successful caches.')
    records=[];cancelled=0;ambiguous=0;counts={c['id']:0 for c in complexes}
    for code,kind,r in allrows:
        matches=[c for c in complexes if c['bjd_code'][:5]==code and m.is_matched(r.get('aptNm',''),c['name']) and dong_matches(c,r.get('umdNm')) and (c['bjd_code'][5:10]=='00000' or not r.get('umdCd') or c['bjd_code'][5:10]==r['umdCd'])]
        if len(matches)!=1:
            if matches:ambiguous+=1
            continue
        if r.get('cdealType') or r.get('cdealDay'):cancelled+=1;continue
        if '직거래' in r.get('dealingGbn',''):continue
        c=matches[0]
        records.append({'complex_id':c['id'],'exclusive_area_exact':float(r['excluUseAr']),'deal_price':int(r['dealAmount'].replace(',',''))*10000,'deal_date':f"{int(r['dealYear']):04d}-{int(r['dealMonth']):02d}-{int(r['dealDay']):02d}",'floor':int(r.get('floor') or 0),'apt_dong':r.get('aptDong'),'apt_seq':r.get('aptSeq'),'source':'molit_'+kind,'transaction_type':('분양권·입주권' if kind=='rights' else '일반 매매'),'build_year':r.get('buildYear'),'ownership_type':r.get('ownershipGbn'),'source_name':r.get('aptNm'),'source_dong':r.get('umdNm'),'match_key_area':round(float(r['excluUseAr']))})
        counts[c['id']]+=1
    if not records:raise RuntimeError('No matching records; refuse to publish an empty backfill')
    doc={'fetched_at':datetime.now(timezone.utc).isoformat(),'from_month':months[0],'to_month':months[-1],'district_months':len(tasks),'cancelled_excluded':cancelled,'ambiguous_complex_excluded':ambiguous,'counts':counts,'transactions':records,'complexes':[{k:c.get(k) for k in ('id','name','bjd_code','address')} for c in complexes]}
    from official_changes import POLICY, compare
    out=CACHE/'verified_full.json'
    previous=json.loads(out.read_text(encoding='utf-8')) if out.exists() else None
    import hashlib
    doc['source_rules']=hashlib.sha256((ROOT/'pipeline/complex_matching.py').read_bytes()+(ROOT/'pipeline/31_daily_rtms_pro.py').read_bytes()).hexdigest()
    doc['refresh_policy']={'mode':refresh_mode,'district_month_pairs':len(refresh_pairs),'reference_months_included':True}
    doc['observation_policy']=POLICY
    changes=compare(previous,doc)
    # Embed comparison and source in the same atomic file; never mix two runs.
    doc['observation_changes']=changes
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8');tmp.replace(out)
    print(json.dumps({k:v for k,v in doc.items() if k not in ('transactions','counts','complexes')},ensure_ascii=True),flush=True)
    print(f'Verified transactions: {len(records)}; complexes with data: {sum(v>0 for v in counts.values())}',flush=True)
if __name__=='__main__':main()
