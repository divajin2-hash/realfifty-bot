import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from daily_type_matching import validate_asks, fetch_type

class DailyMatchingTests(unittest.TestCase):
    def test_disappearing_types_stop_publication(self):
        with self.assertRaises(ValueError):
            validate_asks([{'naver_complex_no': '1', 'ptp_no': '2'}], {'types': {'1:2': {}, '1:3': {}}})

    def test_api_failure_does_not_write_empty_cache(self):
        with patch('daily_type_matching.requests.Session') as session, patch('daily_type_matching.time.sleep'):
            session.return_value.__enter__.return_value.get.return_value.status_code = 503
            cache = MagicMock(spec=Path)
            with self.assertRaises(RuntimeError):
                fetch_type({'naver_complex_no': '1', 'ptp_no': '2'}, cache)
            cache.__truediv__.assert_not_called()

if __name__ == '__main__':
    unittest.main()
