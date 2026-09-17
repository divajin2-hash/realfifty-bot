import sys, unittest, json, shutil, uuid
from contextlib import contextmanager
from pathlib import Path
from datetime import date
from unittest.mock import Mock,patch
sys.path.insert(0,str(Path(__file__).resolve().parent))
from factcheck_core import analyze,collect,months,normalize,validate_scope
from research_core import validate_report,change,snapshot

def scope(**kw):
 return dict(lawd_code='11710',district='서울 송파구',dong='잠실동',start='2026-06-01',end='2026-06-30',baseline_start='2026-05-01',baseline_end='2026-05-31',metric='price_direction',direction='up',scope_confirmed=True,claim='잠실동 아파트 가격 상승')|kw
def row(month=6,amount='110,000',**kw):
 return dict(dealYear='2026',dealMonth=str(month),dealDay='10',aptNm='테스트',aptSeq='test',umdNm='잠실동',jibun='1',excluUseAr='84.99',dealAmount=amount,floor='7',dealingGbn='중개거래',cdealType='',cdealDay='')|kw

@contextmanager
def test_directory():
 root=Path(__file__).resolve().parent
 target=root/('.test-research-'+uuid.uuid4().hex)
 target.mkdir()
 try:yield target
 finally:
  resolved=target.resolve()
  if resolved.parent==root and resolved.name.startswith('.test-research-'):
   shutil.rmtree(resolved)
class ResearchTests(unittest.TestCase):
 def test_direction_uses_baseline_median(self):
  raw=[row(5,'100,000'),row(5,'100,000')]+[row() for _ in range(20)]
  r=analyze(raw,scope(),date(2026,9,16));self.assertEqual(r['stats']['up'],20);self.assertEqual(r['verdict'],'상승 거래 우세');self.assertEqual(r['rows'][0]['baseline_median'],1000000000)
 def test_cancel_direct_unknown_missing_exact_area(self):
  raw=[row(5,'100,000'),row(5,'100,000'),row(),row(cdealType='O'),row(dealingGbn='직거래'),row(dealingGbn=''),row(excluUseAr='84.98'),row(floor='14'),row(umdNm='다른동')]
  r=analyze(raw,scope(),date(2026,9,16));s=r['stats'];self.assertEqual(s['current_count'],5);self.assertEqual(s['cancelled'],1);self.assertEqual(s['direct'],1);self.assertEqual(s['unknown_type'],1);self.assertEqual(s['up'],1);self.assertEqual(s['unmatched'],2);self.assertEqual(r['verdict'],'판단 유보')
 def test_provisional_never_definitive(self):
  r=analyze([row(5,'100,000')]*2+[row()]*25,scope(),date(2026,7,5));self.assertTrue(r['provisional']);self.assertEqual(r['verdict'],'판단 유보')
 def test_volume_zero_and_population(self):
  r=analyze([row(5)]*20,scope(metric='volume_change',direction='down'),date(2026,9,16));self.assertEqual(r['stats']['volume_change'],-100);self.assertEqual(r['verdict'],'범위 내 일치')
 def test_invalid_period_and_months(self):
  with self.assertRaises(ValueError):validate_scope(scope(baseline_end='2026-06-05'))
  with self.assertRaises(ValueError):validate_scope(scope(metric='volume_change',start='2026-06-10'))
  self.assertEqual(months('2025-12-01','2026-02-01'),['202512','202601','202602'])
 def test_pagination_complete_and_failure(self):
  def xml(n,rows):return f'<response><header><resultCode>000</resultCode></header><body><totalCount>{n}</totalCount><items>{rows}</items></body></response>'.encode()
  session=Mock();session.get.side_effect=[Mock(status_code=200,content=xml(2,'<item><aptNm>A</aptNm></item>')),Mock(status_code=200,content=xml(2,'<item><aptNm>B</aptNm></item>'))]
  rows,meta=collect('11710','202606','test',session);self.assertEqual(len(rows),2);self.assertEqual(meta['pages'],2)
  session=Mock();session.get.return_value=Mock(status_code=200,content=xml(2,''))
  with self.assertRaises(RuntimeError):collect('11710','202606','test',session)
 def test_report_fails_on_invented_numbers(self):
  with self.assertRaises(ValueError):validate_report({'title':'가격 99% 상승','summary':'요약'},set())
  self.assertIsNone(change(0,100));self.assertIsNone(change(100,0))
 def test_snapshot_real_data(self):
  d=snapshot();self.assertEqual(d['count'],50);self.assertEqual(d['typeCount'],732);self.assertGreater(d['meanDrop'],-100);self.assertEqual(d['below'],sum(r['gap']<0 for r in d['comparable']))
 def test_queue_processes_confirmed_job_and_preserves_success(self):
  from factcheck_core import run
  with test_directory() as temp:
   base=Path(temp)/'factcheck';queue=base/'queue';queue.mkdir(parents=True)
   jobid='a'*32;job={'id':jobid,'article':{'id':'test','title':'개발 테스트','link':'https://example.com'},'scope':scope()}
   (queue/f'{jobid}.json').write_text(json.dumps(job),encoding='utf-8')
   def response(lawd,month,key,session):
    rows=[row(5,'100,000')]*2 if month=='202605' else [row()]*20
    return rows,{'lawd_code':lawd,'month':month,'total':len(rows),'pages':1}
   with patch('factcheck_core.DATA',Path(temp)),patch('factcheck_core.collect',side_effect=response),patch('sys.argv',['41_ai_news_factcheck.py']),patch('dotenv.load_dotenv'),patch('os.getenv',return_value='test'):
    run()
   output=base/'results'/f'{jobid}.json';first=output.read_text(encoding='utf-8');result=json.loads(first)
   self.assertEqual(result['status'],'collected');self.assertEqual(result['stats']['up'],20);self.assertEqual(len(result['source_sha256']),64)
   self.assertTrue((base/'raw'/f'{jobid}.json').exists())
   with patch('factcheck_core.DATA',Path(temp)),patch('factcheck_core.collect',side_effect=RuntimeError('API unavailable')),patch('sys.argv',['41_ai_news_factcheck.py','--retry']),patch('dotenv.load_dotenv'),patch('os.getenv',return_value='test'):
    run()
   self.assertEqual(output.read_text(encoding='utf-8'),first)
if __name__=='__main__':unittest.main(verbosity=2)
