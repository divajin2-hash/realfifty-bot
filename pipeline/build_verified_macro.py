"""Build monthly observations from the same matched trades used by the UI."""
import json
import statistics
from collections import defaultdict
from pathlib import Path

def timeline(groups):
    monthly = defaultdict(dict)
    for group in groups:
        for stat in group['stats']:
            peak = stat.get('highest_deal_price') or 0
            if peak <= 0:
                continue
            for trade in stat.get('all_trades_history', []):
                if not trade.get('date') or not trade.get('price'):
                    continue
                key = (group['complex']['id'], trade.get('id') or
                       (trade.get('exclusive_area_exact'), trade['date'], trade['price'], trade.get('floor'), trade.get('type')))
                # Shared-area floor plans must not multiply the same transaction.
                monthly[trade['date'][:7]].setdefault(key, []).append(trade['price'] / peak * 100)
    return [{'month': month, 'sample_count': len(rows),
             'recovery_rate': round(statistics.median(statistics.median(v) for v in rows.values()), 2)}
            for month, rows in sorted(monthly.items()) if rows]

if __name__ == '__main__':
    data = Path(__file__).resolve().parents[1] / 'web/src/data'
    result = timeline(json.loads((data / 'kb50_stats.json').read_text(encoding='utf-8-sig')))
    target = data / 'macro_tx_index.json'
    temp = target.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    temp.replace(target)
    print(f'Verified macro: {len(result)} months')
