"""Shared, deterministic research snapshot. No API calls or env loading on import."""
import json, math, os, re
from pathlib import Path
from datetime import datetime, timezone, timedelta
KST=timezone(timedelta(hours=9))
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'web/src/data'
def positive(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) and x>0
def change(value,base):return (value/base-1)*100 if positive(value) and positive(base) else None
def age(value,asof):
 try:
  result=(asof.date()-datetime.fromisoformat(value[:10]).date()).days
  return result if result>=0 else None
 except (ValueError,TypeError):return None
def representative(stats,asof):
 candidates=[s for s in stats if positive(s.get('current_lowest_ask')) and positive((s.get('recent_deal_absolute')or{}).get('price'))] or stats
 def key(s):
  days=age((s.get('recent_deal_absolute')or{}).get('date'),asof)
  days=days if days is not None else float('inf')
  return (days>365,abs((s.get('exclusive_area')or s.get('match_key_area')or 0)-84),days)
 return min(candidates,key=key) if candidates else None
def snapshot(data_dir=DATA):
 source=Path(data_dir)/'kb50_stats.json'
 groups=json.loads(source.read_text(encoding='utf-8-sig'))
 stamp=groups[0].get('generated_at') if groups else None
 if not stamp or any(g.get('generated_at')!=stamp for g in groups):
  raise ValueError('Missing or inconsistent data generation timestamp')
 asof=datetime.fromisoformat(stamp).astimezone(KST)
 rows=[]
 for g in groups:
  s=representative(g['stats'],asof) or {};t=s.get('recent_deal_absolute')or{}
  area=s.get('exclusive_area')or s.get('match_key_area')or 0
  area_text=f'{area:g}'
  rows.append(dict(id=g['complex']['id'],name=g['complex']['name'],address=g['complex'].get('address',''),area=f"{s.get('naver_ptp_no')or''}:{s.get('pyeong_name')or''}:{area_text}",areaLabel=f'전용 {area_text}㎡',trade=t.get('price'),tradeDate=t.get('date'),ask=s.get('current_lowest_ask')or None,peak=s.get('highest_deal_price')or None,age=age(t.get('date'),asof),gap=change(s.get('current_lowest_ask'),t.get('price')),drop=change(t.get('price'),s.get('highest_deal_price')),askDrop=change(s.get('current_lowest_ask'),s.get('highest_deal_price'))))
 comparable=[r for r in rows if r['gap'] is not None and r['age'] is not None and r['age']<=365]
 def mean(key):
  values=[r[key] for r in comparable if r[key] is not None]
  return sum(values)/len(values) if values else None
 macro=Path(data_dir)/'macro_tx_index.json';series=json.loads(macro.read_text(encoding='utf-8-sig')) if macro.exists() else []
 month=asof.strftime('%Y-%m');series=sorted([p for p in series if p['month']<=month],key=lambda p:p['month'])
 complete=[p for p in series if p['month']<month]
 return dict(updatedAt=asof.isoformat(),rows=rows,comparable=comparable,count=len(rows),typeCount=sum(len(g['stats']) for g in groups),coveredTypes=sum(positive(s.get('current_lowest_ask')) for g in groups for s in g['stats']),meanDrop=mean('drop'),meanGap=mean('gap'),meanAskDrop=mean('askDrop'),below=sum(r['gap']<0 for r in comparable),stale=sum(r['age'] is None or r['age']>365 for r in rows),series=series[-36:],latest=series[-1] if series else None,lastComplete=complete[-1] if complete else None,month=month)
def evidence(d):
 return {'gap':{'label':'평균 호가 괴리 (%)','value':d['meanGap'],'n':len(d['comparable'])},'drop':{'label':'관측 고점 대비 최근 실거래 평균 (%)','value':d['meanDrop'],'n':len(d['comparable'])},'below':{'label':'실거래 아래 호가 단지 수','value':d['below'],'n':len(d['comparable'])},'coverage':{'label':'호가 수집 타입 수','value':d['coveredTypes'],'n':d['typeCount']},'monthly':{'label':'최근 월 신고 집계 (미완결 가능)','value':d['latest']},'complete_month':{'label':'직전 완료 월 집계 (신고 지연 가능)','value':d['lastComplete']}}
def atomic_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');temp.replace(path)
def generate_json(prompt,payload):
 from dotenv import load_dotenv
 import requests
 load_dotenv(ROOT/'pipeline/.env')
 key=os.getenv('GEMINI_API_KEY');model=os.getenv('GEMINI_MODEL','gemini-3.6-flash')
 if not key:raise RuntimeError('GEMINI_API_KEY가 설정되지 않았습니다.')
 if not re.fullmatch(r'gemini-[a-zA-Z0-9.\-]+',model):raise ValueError('잘못된 GEMINI_MODEL')
 try:
  response=requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':key},json={'systemInstruction':{'parts':[{'text':prompt}]},'contents':[{'role':'user','parts':[{'text':json.dumps(payload,ensure_ascii=False,allow_nan=False)}]}],'generationConfig':{'temperature':0.2,'responseMimeType':'application/json'}},timeout=120)
 except requests.RequestException:raise RuntimeError('Gemini 연결 실패') from None
 if response.status_code!=200:raise RuntimeError(f'Gemini HTTP {response.status_code}; 기존 결과 보존')
 try:
  candidate=response.json()['candidates'][0]
  if candidate.get('finishReason')!='STOP':raise ValueError('incomplete')
  text=''.join(p.get('text','') for p in candidate['content']['parts'] if not p.get('thought'))
  return json.loads(text),model
 except (KeyError,IndexError,TypeError,ValueError):raise RuntimeError('Gemini JSON 응답 불완전; 기존 결과 보존') from None
def validate_report(r,ids):
 def text(s):
  if not isinstance(s,str) or not s.strip() or len(s)>5000 or re.search(r'\d',s):raise ValueError('보고서 서술에는 새 수치를 넣을 수 없습니다.')
 for key in ('title','summary'):text(r.get(key))
 for key,lo,hi in [('takeaways',3,3),('analysis',2,4)]:
  items=r.get(key)
  if not isinstance(items,list) or not lo<=len(items)<=hi:raise ValueError('보고서 섹션 수 오류')
  for item in items:
   text(item.get('title'));text(item.get('body'))
   refs=item.get('evidence_ids')
   if not isinstance(refs,list) or not refs or any(ref not in ids for ref in refs):raise ValueError('근거 ID 오류')
 if not isinstance(r.get('scenarios'),list) or not 2<=len(r['scenarios'])<=3:raise ValueError('시나리오 수 오류')
 for item in r['scenarios']:
  for key in ('title','condition','implication'):text(item.get(key))
 if not isinstance(r.get('limitations'),list) or not r['limitations']:raise ValueError('한계 누락')
 for item in r['limitations']:text(item)
 return r
def run_report():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true',help='AI 호출 없이 계산 결과만 확인');args=parser.parse_args()
 d=snapshot();facts=evidence(d)
 if args.preview:
  print(json.dumps(facts,ensure_ascii=False,indent=2));return
 prompt=(ROOT/'pipeline/prompts/daily_report.md').read_text(encoding='utf-8')
 report,model=generate_json(prompt,{'as_of':d['updatedAt'],'scope':'RealFifty 선정 단지 표본','evidence':facts})
 validate_report(report,set(facts))
 now=datetime.now(KST);date=now.strftime('%Y-%m-%d')
 result={'matching_version':'area-v3','schema_version':2,'date':date,'generated_at':now.isoformat(),'model':model,'prompt_version':'research-v2','snapshot':d,'evidence':facts,'report':report}
 atomic_json(DATA/'reports'/f'report_{date}.json',result)
 lines=[f"# {report['title']}",report['summary'],f"기준: {d['updatedAt']} | 모델: {model}",'## 주요 근거']
 for key,fact in facts.items():lines.append(f"- [{key}] {fact['label']}: {json.dumps(fact['value'],ensure_ascii=False)}")
 for section in ['takeaways','analysis']:
  for item in report[section]:lines.extend([f"## {item['title']}",item['body'],f"근거: {', '.join(item['evidence_ids'])}"])
 lines.append('## 조건부 시나리오')
 for s in report['scenarios']:lines.extend([f"### {s['title']}",s['condition'],s['implication']])
 lines.extend(['## 분석 한계',*report['limitations']])
 path=DATA/'reports'/f'report_{date}.md';tmp=path.with_suffix('.md.tmp');tmp.write_text('\n\n'.join(lines),encoding='utf-8');tmp.replace(path)
 print(f'Report saved: {date} ({model})')
