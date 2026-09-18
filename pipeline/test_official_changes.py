import unittest
from official_changes import POLICY, compare, validate_groups

class OfficialChangesTest(unittest.TestCase):
    def doc(self, rows):
        return dict(observation_policy=POLICY,fetched_at='2026-09-18T00:00:00+00:00',from_month='201401',to_month='202609',complexes=[{'id':'a'}],transactions=rows)
    def trade(self, price=100):
        return dict(complex_id='a',deal_date='2026-09-01',exclusive_area_exact=84.92,deal_price=price,floor=2,source='molit_apt')
    def test_first_run_is_not_new_transactions(self):
        self.assertEqual(compare(None,self.doc([self.trade()]))['status'],'baseline')
    def test_reordering_and_raw_ids_do_not_create_changes(self):
        a,b=self.trade(),self.trade(200)
        new=dict(a,id='different-id')
        self.assertEqual(compare(self.doc([a,b]),self.doc([b,new]))['added'],0)
    def test_duplicate_contracts_count_without_type_multiplication(self):
        self.assertEqual(compare(self.doc([self.trade()]),self.doc([self.trade(),self.trade()]))['added'],1)
    def test_correction_is_added_and_removed_not_price_rise(self):
        x=compare(self.doc([self.trade()]),self.doc([self.trade(200)]))
        self.assertEqual((x['added'],x['removed']),(1,1))
    def test_scope_change_holds_comparison(self):
        a,b=self.doc([]),self.doc([]);b['to_month']='202610'
        self.assertEqual(compare(a,b)['status'],'scope_changed')
    def test_cancelled_display_is_rejected(self):
        groups=[{'complex':{'id':'a'},'stats':[{'all_trades_history':[{'date':'2026-09-01','price':100,'floor':2,'exclusive_area_exact':84.92,'type':'일반 매매'}]}]}]
        validate_groups(groups,self.doc([self.trade()]))
        with self.assertRaises(ValueError):validate_groups(groups,self.doc([]))

    def test_mapping_rule_change_holds_comparison(self):
        a,b=self.doc([]),self.doc([]);a['source_rules']='old';b['source_rules']='new'
        self.assertEqual(compare(a,b)['status'],'scope_changed')

    def test_stale_and_mixed_ai_inputs_are_rejected(self):
        from official_changes import require_current_source
        with self.assertRaises(ValueError):require_current_source([], dict(self.doc([]),fetched_at='2000-01-01T00:00:00+00:00'))
        from datetime import datetime, timezone
        doc=dict(self.doc([]),fetched_at=datetime.now(timezone.utc).isoformat())
        with self.assertRaises(ValueError):require_current_source([{'official_observed_at':'other'}],doc)

if __name__=='__main__':unittest.main()
