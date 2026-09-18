import unittest
from datetime import date
from rtms_refresh_policy import plan_refresh

class RefreshPolicyTests(unittest.TestCase):
    cs=[{'id':'a','bjd_code':'1165010600'},{'id':'b','bjd_code':'1165010700'}]
    def test_daily_three_months_deduplicated(self):
        mode,pairs=plan_refresh(date(2026,9,18),self.cs,[])
        self.assertEqual(mode,'daily')
        self.assertEqual(pairs,{('11650',m) for m in ['202607','202608','202609']})
    def test_weekly_twelve_months(self):
        mode,pairs=plan_refresh(date(2026,9,13),self.cs,[])
        self.assertEqual(mode,'weekly');self.assertEqual(len(pairs),12)
        self.assertIn(('11650','202510'),pairs)
    def test_first_sunday_full(self):
        mode,pairs=plan_refresh(date(2026,9,6),self.cs,[])
        self.assertEqual(mode,'full');self.assertEqual(len(pairs),153)
    def test_year_boundary(self):
        _,pairs=plan_refresh(date(2027,1,1),self.cs,[])
        self.assertEqual(pairs,{('11650',m) for m in ['202611','202612','202701']})
    def test_old_recent_and_peak_always_refresh(self):
        groups=[{'complex':{'id':'a'},'stats':[{'recent_deal_absolute':{'date':'2022-02-10'},'highest_deal_date':'2021-11-15'}]*2}]
        _,pairs=plan_refresh(date(2026,9,18),self.cs,groups)
        self.assertEqual(len(pairs),5)
        self.assertIn(('11650','202202'),pairs);self.assertIn(('11650','202111'),pairs)
    def test_explicit_full_refresh(self):
        mode,pairs=plan_refresh(date(2026,9,18),self.cs,[],True)
        self.assertEqual(mode,'full');self.assertIn(('11650','201401'),pairs)
    def test_unknown_complex_blocks(self):
        with self.assertRaises(ValueError):plan_refresh(date(2026,9,18),self.cs,[{'complex':{'id':'other'},'stats':[]}])

if __name__=='__main__':unittest.main()
