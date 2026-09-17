import unittest
from build_verified_macro import timeline

class VerifiedMacroTests(unittest.TestCase):
    def test_shared_type_does_not_duplicate_trade(self):
        trade = {'id': 'one', 'date': '2026-09-01', 'price': 80}
        stat = {'highest_deal_price': 100, 'all_trades_history': [trade]}
        result = timeline([{'complex': {'id': 'a'}, 'stats': [stat, stat]}])
        self.assertEqual(result, [{'month': '2026-09', 'sample_count': 1, 'recovery_rate': 80.0}])

    def test_same_signature_different_complex_is_preserved(self):
        stat = {'highest_deal_price': 100, 'all_trades_history': [{'id': 'one', 'date': '2026-09-01', 'price': 80}]}
        result = timeline([{'complex': {'id': c}, 'stats': [stat]} for c in ['a', 'b']])
        self.assertEqual(result[0]['sample_count'], 2)
