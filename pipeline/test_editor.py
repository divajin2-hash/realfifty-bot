import importlib.util,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
p=Path(__file__).resolve().with_name('42_factcheck_editor.py');spec=importlib.util.spec_from_file_location('editor',p);editor=importlib.util.module_from_spec(spec);spec.loader.exec_module(editor)
class ScopeTests(unittest.TestCase):
 def test_reject_title_guess(self):
  with self.assertRaises(ValueError):editor.validate_extraction({'supported':True,'property_type':'apartment','date_basis':'contract','scope':{},'evidence':{}},'본문',{})
 def test_reject_unsupported(self):
  with self.assertRaises(ValueError):editor.validate_extraction({'supported':False,'reason':'가격지수'},'본문',{})
 def test_google_link_not_body(self):
  with self.assertRaises(ValueError):editor.article_text('https://news.google.com/rss/articles/test')
 def test_non_https(self):
  with self.assertRaises(ValueError):editor.public_url('http://localhost/a')
 def test_direction_scope(self):
  scope={'lawd_code':'11710','dong':'','start':'2026-06-01','end':'2026-06-30','baseline_start':'2026-05-01','baseline_end':'2026-05-31','claim':'송파구 아파트 매매 거래량이 증가했다','metric':'volume_change','direction':'up'}
  quotes={'region':'서울 송파구','period':'2026년 6월','baseline':'2026년 5월','claim':'거래량이 증가했다','property_type':'아파트 매매'}
  s,_=editor.validate_extraction({'supported':True,'property_type':'apartment','date_basis':'contract','scope':scope,'evidence':quotes},' '.join(quotes.values()),{'11710':'서울 송파구'})
  self.assertTrue(s['scope_confirmed'])
  quotes['period']='없는 본문 구절'
  with self.assertRaises(ValueError):editor.validate_extraction({'supported':True,'property_type':'apartment','date_basis':'contract','scope':scope,'evidence':quotes},'서울 송파구',{'11710':'서울 송파구'})
if __name__=='__main__':unittest.main()
