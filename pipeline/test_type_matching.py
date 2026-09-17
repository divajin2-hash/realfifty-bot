import unittest
from unittest.mock import patch
from type_matching import match_trades,trade_key
from complex_matching import dong_matches
from build_type_trade_evidence import resolve_area
from decimal import Decimal as D
class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.ask={'naver_complex_no':'1','ptp_no':'1','exclusive_area':84.99}
        self.trade={'deal_date':'2026-01-01','deal_price':1000000000,'floor':5,'exclusive_area_exact':84.9984,'source':'molit_apt'}
    def test_evidence_is_transaction_specific(self):
        entry={'1:1':{'asking_area':84.99,'trade_keys':[trade_key(self.trade)]}}
        unseen={**self.trade,'deal_date':'2026-01-02'}
        other_kind={**self.trade,'source':'molit_rights'}
        with patch('type_matching.load_evidence',return_value=entry):
            found,meta=match_trades(self.ask,[self.ask],[self.trade,unseen,other_kind])
        self.assertEqual(found,[self.trade]);self.assertEqual(meta['crosschecked_trade_count'],1)
    def test_type_area_change_invalidates_evidence(self):
        with patch('type_matching.load_evidence',return_value={'1:1':{'asking_area':84.98,'trade_keys':[trade_key(self.trade)]}}):
            self.assertEqual(match_trades(self.ask,[self.ask],[self.trade])[0],[])
    def test_nearby_area_not_assigned(self):
        with patch('type_matching.load_evidence',return_value={}):
            self.assertEqual(match_trades(self.ask,[self.ask],[self.trade])[0],[])
    def test_shared_area_stays_shared(self):
        t={**self.trade,'exclusive_area_exact':84.99};other={**self.ask,'ptp_no':'2'}
        with patch('type_matching.load_evidence',return_value={}):
            found,meta=match_trades(self.ask,[self.ask,other],[t])
        self.assertEqual(found,[t]);self.assertEqual(meta['status'],'shared_area')
    def test_dong_exception_is_scoped(self):
        c={'name':'래미안슈르','bjd_code':'4129000000','region':'경기 원문동'}
        self.assertTrue(dong_matches(c,'별양동'));self.assertFalse(dong_matches(c,'중앙동'))
        self.assertFalse(dong_matches({**c,'name':'다른 단지'},'별양동'))
class CandidateResolutionTests(unittest.TestCase):
    def test_exact_raw_area(self):
        self.assertEqual(resolve_area({D('84.97'),D('84.98')},84.98,set()),(D('84.98'),'exact_original_area'))
    def test_independent_anchor(self):
        self.assertEqual(resolve_area({D('84.705'),D('84.751')},84.70,{D('84.705')}),(D('84.705'),'independent_trade_area'))
    def test_no_nearest_guess(self):
        self.assertEqual(resolve_area({D('84.705'),D('84.751')},84.70,set()),(None,None))
    def test_conflicting_anchors_stay_unresolved(self):
        self.assertEqual(resolve_area({D('84.705'),D('84.751')},84.70,{D('84.705'),D('84.751')}),(None,None))
if __name__=='__main__':unittest.main()
