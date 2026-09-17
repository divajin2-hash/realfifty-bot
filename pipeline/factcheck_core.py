"""Paginated district-level MOLIT collection and reproducible scoped comparisons."""
import calendar, json, re, statistics, hashlib
from collections import defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote
import xml.etree.ElementTree as ET
from research_core import DATA,ROOT,KST,atomic_json,generate_json,change
ENDPOINT='https://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
def months(start,end):
 y,m=map(int,start[:7].split('-'));ey,em=map(int,end[:7].split('-'));out=[]
 while (y,m)<=(ey,em):
  out.append(f'{y:04d}{m:02d}');m+=1
  if m==13:y+=1;m=1
 return out
def collect(lawd,month,key,session):
 rows=[];page=1;expected=None
 while True:
  try:
   response=session.get(ENDPOINT,params={'serviceKey':unquote(key),'LAWD_CD':lawd,'DEAL_YMD':month,'numOfRows':1000,'pageNo':page},timeout=30)
   if response.status_code!=200:raise RuntimeError(f'실거래 API HTTP {response.status_code}')
   root=ET.fromstring(response.content)
  except Exception:raise RuntimeError('실거래 API 연결 또는 XML 파싱 실패') from None
  code=root.findtext('.//resultCode')
  if code not in ('000','00','0'):raise RuntimeError('실거래 API 응답 오류. 키 권한 및 사용량을 확인하세요.')
  total=root.findtext('.//totalCount')
  if total is None:raise RuntimeError('API totalCount 누락')
  total=int(total)
  if expected is not None and expected!=total:raise RuntimeError('수집 중 원자료 건수 변경. 다시 수집하세요.')
  expected=total;items=root.findall('.//item')
  if not items and len(rows)<total:raise RuntimeError('API 페이지 누락')
  rows.extend([{n.tag:(n.text or '').strip() for n in item} for item in items])
  if len(rows)>=total:
   if len(rows)!=total:raise RuntimeError('API 건수 불일치')
   break
  page+=1
  if page>200:raise RuntimeError('페이지 상한 초과')
 return rows,{'lawd_code':lawd,'month':month,'total':total,'pages':page}
def normalize(raw):
 try:
  day=date(int(raw['dealYear']),int(raw['dealMonth']),int(raw['dealDay'])).isoformat()
  area=Decimal(raw['excluUseAr']);price=int(raw['dealAmount'].replace(',',''))*10000;floor=int(raw['floor'])
  if area<=0 or price<=0 or not raw.get('aptNm') or not raw.get('umdNm'):return None
  identity=raw.get('aptSeq') or '|'.join([raw.get('umdNm',''),raw.get('jibun',''),raw['aptNm']])
  # Keep indistinguishable source rows: no stable transaction ID is provided.
  return {'date':day,'name':raw['aptNm'],'dong':raw['umdNm'],'area':float(area),'floor':floor,'price':price,'key':(identity,str(area.normalize()),(floor-1)//5),'cancelled':raw.get('cdealType','') in ('O','Y','1') or raw.get('cdealDay','') not in ('','-'),'type':raw.get('dealingGbn','')}
 except (KeyError,ValueError,ArithmeticError):return None
def validate_scope(s):
 if not re.fullmatch(r'\d{5}',s.get('lawd_code','')) or s.get('scope_confirmed') is not True:raise ValueError('확정된 지역 코드가 필요합니다.')
 ds=[date.fromisoformat(s[k]) for k in ('start','end','baseline_start','baseline_end')]
 start,end,bs,be=ds
 if not bs<=be<start<=end<=datetime.now(KST).date() or (end-bs).days>730:raise ValueError('검증 기간 오류')
 if s.get('metric') not in ('price_direction','volume_change') or s.get('direction') not in ('up','down'):raise ValueError('검증 지표 오류')
 if s['metric']=='volume_change':
  full=lambda a,b:a.day==1 and b.day==calendar.monthrange(b.year,b.month)[1]
  length=lambda a,b:(b.year-a.year)*12+b.month-a.month
  if (end-start).days!=(be-bs).days and not(full(start,end) and full(bs,be) and length(start,end)==length(bs,be)):raise ValueError('거래량은 동일 길이 기간만 비교합니다.')
 return s
def analyze(raw,scope,asof=None):
 validate_scope(scope);asof=asof or datetime.now(KST).date();stats={'cancelled':0,'direct':0,'unknown_type':0,'invalid':0}
 valid=[]
 for source in raw:
  if scope.get('dong') and source.get('umdNm','').strip()!=scope['dong']:continue
  row=normalize(source)
  if not row:stats['invalid']+=1;continue
  if not (scope['start']<=row['date']<=scope['end'] or scope['baseline_start']<=row['date']<=scope['baseline_end']):continue
  if row['cancelled']:stats['cancelled']+=1;continue
  if row['type']=='직거래':stats['direct']+=1
  if row['type'] not in ('중개거래','직거래'):stats['unknown_type']+=1
  valid.append(row)
 current=[r for r in valid if scope['start']<=r['date']<=scope['end']]
 baseline=[r for r in valid if scope['baseline_start']<=r['date']<=scope['baseline_end']]
 buckets=defaultdict(list)
 for r in baseline:
  if r['type']=='중개거래':buckets[r['key']].append(r['price'])
 counts={'up':0,'down':0,'flat':0,'unmatched':0};evidence=[]
 for r in current:
  if r['type']!='중개거래':continue
  values=buckets[r['key']];median=statistics.median(values) if len(values)>=2 else None
  gap=change(r['price'],median);direction='unmatched' if gap is None else 'up' if gap>1 else 'down' if gap< -1 else 'flat'
  counts[direction]+=1;evidence.append({k:v for k,v in r.items() if k not in ('key','cancelled','type')}|{'baseline_median':median,'change':gap,'direction':direction})
 n=counts['up']+counts['down']+counts['flat'];total=n+counts['unmatched'];coverage=n/total if total else 0
 stats.update(counts);stats.update(current_count=len(current),baseline_count=len(baseline),volume_change=change(len(current),len(baseline)) if current else (-100.0 if baseline else None),comparable=n,price_candidates=total,coverage=coverage)
 provisional=(asof-date.fromisoformat(scope['end'])).days<31
 verdict='판단 유보';reason='비교 가능한 근거가 충분히 확보되지 않았습니다.'
 if provisional:reason='대상 기간 종료 후 신고 기간이 충분히 지나지 않아 잠정 집계만 제공합니다.'
 elif stats['invalid']:reason='필수값이 없는 원자료가 있어 집계의 완전성을 확인해야 합니다.'
 elif scope['metric']=='price_direction':
  if n>=20 and coverage>=.6:
   direction='up' if counts['up']/n>=.6 else 'down' if counts['down']/n>=.6 else 'mixed'
   verdict='상승 거래 우세' if direction=='up' else '하락 거래 우세' if direction=='down' else '혼재'
   reason='동일 단지·면적·층 구간 기준의 비교 가능한 거래 분포에 한정한 결과입니다. 기사 전체나 지역 가격지수의 진위를 뜻하지 않습니다.'
  else:reason='가격 비교는 비교 가능 거래 20건 이상·비교율 60% 이상일 때만 방향성을 요약합니다.'
 elif stats['baseline_count']>=20 and stats['volume_change'] is not None:
  delta=stats['volume_change'];direction='up' if delta>0 else 'down' if delta<0 else 'flat'
  verdict='범위 내 일치' if direction==scope['direction'] else '상반 근거' if direction!='flat' else '변화 없음'
  reason='설정한 동일 길이 계약기간의 신고 거래 건수에 한정한 결과입니다. 가격 방향이나 전국 통계를 판정하지 않습니다.'
 return {'stats':stats,'rows':sorted(evidence,key=lambda r:r['date'],reverse=True),'verdict':verdict,'reason':reason,'provisional':provisional}
METHOD=['MOLIT 아파트 매매 상세 API를 시군구·계약 월별로 모든 페이지 조회한 뒤 법정동과 기간을 필터링합니다.','해제 거래 제외. 거래량은 유효 계약 전체(직거래 포함), 가격 비교는 중개거래만 사용합니다.','가격 기준: 동일 단지 식별자(없으면 동·지번·이름), 정확한 전용면적, 5개 층 구간. 비교 기간의 거래 2건 이상 중위가격과 비교합니다.','±1% 이내 보합. 비교 가능 20건·비교율 60% 이상, 방향별 60% 이상일 때 우세로 요약합니다. 통계적 유의성 검정은 아닙니다.','고유 거래 ID가 없어 동일 일자·가격의 행을 임의 중복 제거하지 않습니다. 원자료의 구분 불가능한 중복 가능성이 남습니다.','자료 미공개 동·향·수리 상태는 통제하지 못합니다. 계약일 기준이며 신고 지연·추후 해제로 수정될 수 있습니다.','RealFifty 표본은 동일 동의 보조 관찰 자료이며 지역 검증 모집단을 대체하지 않습니다.']
def run():
 import argparse,os,requests
 from dotenv import load_dotenv
 parser=argparse.ArgumentParser();parser.add_argument('--process-queue',action='store_true');parser.add_argument('--ai',action='store_true');parser.add_argument('--retry',action='store_true');parser.add_argument('--limit',type=int,default=3);args=parser.parse_args()
 base=DATA/'factcheck';queue=base/'queue'
 load_dotenv(ROOT/'pipeline/.env');key=os.getenv('RTMS_API_KEY')
 if not key:raise RuntimeError('RTMS_API_KEY가 필요합니다.')
 if not queue.exists():print('검증 요청이 없습니다.');return
 session=requests.Session();count=0
 for file in sorted(queue.glob('*.json'),key=lambda p:p.stat().st_mtime):
  if not re.fullmatch(r'[a-f0-9]{32}\.json',file.name):continue
  out=base/'results'/file.name
  if out.exists() and not args.retry:continue
  if count>=max(1,min(args.limit,20)):break
  job=json.loads(file.read_text(encoding='utf-8'));count+=1
  result={'schema_version':2,'job_id':job['id'],'article':job['article'],'scope':job['scope'],'collected_at':datetime.now(KST).isoformat()}
  try:
   scope=validate_scope(job['scope']);raw=[];sources=[]
   requested=sorted(set(months(scope['start'],scope['end'])+months(scope['baseline_start'],scope['baseline_end'])))
   for month in requested:
    batch,meta=collect(scope['lawd_code'],month,key,session);raw.extend(batch);sources.append(meta)
   result.update(analyze(raw,scope));result.update(status='collected',sources=sources,method=METHOD)
   raw_bytes=json.dumps(raw,ensure_ascii=False,sort_keys=True).encode('utf-8')
   result['source_sha256']=hashlib.sha256(raw_bytes).hexdigest()
   atomic_json(base/'raw'/file.name,raw)
   if args.ai:
    try:
     commentary,model=generate_json((ROOT/'pipeline/prompts/factcheck.md').read_text(encoding='utf-8'),{'claim':scope['claim'],'scope':scope,'deterministic_verdict':result['verdict'],'reason':result['reason'],'stats':result['stats'],'method':METHOD})
     texts=[commentary.get('summary'),*(commentary.get('limitations')or[])]
     if len(texts)<2 or any(not isinstance(t,str) or not t.strip() or re.search(r'\d',t) for t in texts):raise ValueError('AI 서술 검증 실패')
     result.update(commentary=commentary,model=model)
    except Exception:result['commentary_status']='AI 서술 생성 실패. 계산 근거만 제공합니다.'
  except Exception:
   result.update(status='error',verdict='판단 유보',error='지역 실거래 수집을 완료하지 못했습니다. API 키 권한, 기간 및 응답을 확인하고 --retry로 재시도하세요.')
  # Preserve successful prior evidence on a failed retry.
  if result['status']=='error' and out.exists() and json.loads(out.read_text(encoding='utf-8')).get('status')=='collected':
   print(f"이전 성공 근거 보존: {job['id']}");continue
  atomic_json(out,result);print(f"{job['id']}: {result['status']}")
