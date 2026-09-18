"""Refresh official sources and transaction-specific type evidence before publishing.

No database writes. Errors stop the caller; source-only missing trades stay excluded.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from curl_cffi import requests
from build_type_trade_evidence import build

ROOT = Path(__file__).resolve().parent

def fetch_type(ask, cache):
    rows = []
    with requests.Session(impersonate='chrome110') as session:
        for page in range(200):
            for attempt in range(3):
                try:
                    response = session.get(
                        'https://fin.land.naver.com/front-api/v1/complex/v2/pyeong/realPrice',
                        params={'complexNumber': ask['naver_complex_no'],
                                'pyeongTypeNumber': ask['ptp_no'], 'tradeType': 'A1',
                                'size': 20, 'page': page}, timeout=30)
                    if response.status_code != 200:
                        raise ValueError('Source HTTP failure')
                    data = response.json()
                    if not data.get('isSuccess'):
                        raise ValueError('Source unsuccessful')
                    result = data['result']
                    batch = result['list']
                    more = result['hasNextPage']
                    if more and not batch:
                        raise ValueError('Incomplete pagination')
                    break
                except Exception:
                    if attempt == 2:
                        raise RuntimeError(f"Type collection failed: {ask['naver_complex_no']}:{ask['ptp_no']} page {page}") from None
                    time.sleep(5 * (attempt + 1))
            rows.extend(batch)
            if not more or (batch and max(r['tradeDate'] for r in batch) < '2014-01-01'):
                break
            time.sleep(.25)
        else:
            raise RuntimeError('Pagination limit reached')
    target = cache / f"{ask['naver_complex_no']}-{ask['ptp_no']}.json"
    target.write_text(json.dumps({'rows': rows, 'retrieved_at': datetime.now().isoformat()}, ensure_ascii=False), encoding='utf-8')

def validate_asks(asks, previous):
    keys = {(str(a['naver_complex_no']), str(a['ptp_no'])) for a in asks}
    if not asks or len(keys) != len(asks):
        raise ValueError('Empty or duplicate type inventory')
    if previous:
        old_keys = {tuple(k.split(':')) for k in previous['types']}
        if old_keys - keys:
            raise ValueError('Types disappeared from collection; review before publishing')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--asks', type=Path, required=True)
    parser.add_argument('--full-refresh', action='store_true')
    parser.add_argument('--offline-cache', type=Path, help='Validation only; never refreshes or publishes')
    args = parser.parse_args()
    asks = json.loads(args.asks.read_text(encoding='utf-8'))
    evidence_path = ROOT / 'type_trade_evidence.json'
    previous = json.loads(evidence_path.read_text(encoding='utf-8')) if evidence_path.exists() else None
    validate_asks(asks, previous)
    cache = args.offline_cache or ROOT / 'rtms_recheck/naver_daily'
    cache.mkdir(parents=True, exist_ok=True)
    if not args.offline_cache:
        command=[sys.executable, str(ROOT / 'recheck_rtms.py')]
        if args.full_refresh:command.append('--full-refresh')
        subprocess.run(command, check=True)
        for i, ask in enumerate(asks, 1):
            fetch_type(ask, cache)
            if i % 50 == 0:
                print(f'Cross-check collected {i}/{len(asks)}', flush=True)
            time.sleep(.2)
    verified = json.loads((ROOT / 'rtms_recheck/verified_full.json').read_text(encoding='utf-8'))
    result = build(asks, verified, cache)
    report = {'checked_at': datetime.now().isoformat(), 'types': len(result['types']),
              'official_trades': len(verified['transactions']),
              'excluded_unresolved': result['unresolved'],
              'resolved_multiple': result['resolved_multiple'],
              'validation_only': bool(args.offline_cache)}
    (ROOT / 'rtms_recheck/matching_status.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if not args.offline_cache:
        temp = evidence_path.with_suffix('.tmp')
        temp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        temp.replace(evidence_path)
    print(f"PASS: {report['types']} types; {len(result['unresolved'])} unsupported display rows excluded")

if __name__ == '__main__':
    main()
