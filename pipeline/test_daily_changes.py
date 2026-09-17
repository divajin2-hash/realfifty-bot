import unittest
from build_daily_changes import build
class ChangesTest(unittest.TestCase):
 def test_type_counts_and_missing(self):
  stats=[dict(naver_complex_no='1',naver_ptp_no=str(i),pyeong_name=str(i),exclusive_area=84.9,match_key_area=85) for i in range(5)]
  groups=[dict(complex=dict(id='id',name='단지'),stats=stats,generated_at='2026-09-17T00:00:00Z')]
  def rows(values):return [dict(naver_complex_no='1',ptp_no=str(i),exclusive_area=84.9,lowest_ask=v) for i,v in enumerate(values)]
  d=build(groups,rows([110,90,0,100]),rows([100,100,100,0]),'2026-09-17','2026-09-16')
  self.assertEqual((d['rises'],d['falls'],d['comparable']),(1,1,2))
  self.assertEqual((d['appeared'],d['disappeared'],d['missing']),(1,1,1))
  self.assertEqual(len(d['rows']),2)
 def test_duplicate_source_rejected(self):
  r=dict(naver_complex_no='1',ptp_no='1')
  with self.assertRaises(ValueError):build([], [r,r], [], 'a','b')
if __name__=='__main__':unittest.main()
