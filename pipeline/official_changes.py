"""Compare official observations, independently of UI type assignments."""
import hashlib
import json
from collections import Counter
from decimal import Decimal

POLICY = 'official-observations-v1'

def identity(t):
    return (str(t['complex_id']), t['deal_date'], str(Decimal(str(t['exclusive_area_exact'])).normalize()),
            int(t['deal_price']), t.get('floor'), t.get('source'), t.get('apt_dong') or '')

def digest(doc):
    return hashlib.sha256(json.dumps(sorted(Counter(identity(t) for t in doc['transactions']).items(), key=str), ensure_ascii=False).encode()).hexdigest()

def compare(previous, current):
    result = {'policy': POLICY, 'observed_at': current['fetched_at'], 'source_digest': digest(current),
              'status': 'baseline', 'added': 0, 'removed': 0}
    if not previous or previous.get('observation_policy') != POLICY:
        return result
    if any(previous.get(k) != current.get(k) for k in ('from_month', 'to_month', 'complexes', 'source_rules')):
        result['status'] = 'scope_changed'
        return result
    before = Counter(identity(t) for t in previous['transactions'])
    after = Counter(identity(t) for t in current['transactions'])
    result.update(status='compared', previous_observed_at=previous['fetched_at'],
                  added=sum((after-before).values()), removed=sum((before-after).values()))
    return result

def validate_groups(groups, official):
    valid = {identity(t)[:6] for t in official['transactions']}
    for group in groups:
        for stat in group['stats']:
            for t in stat.get('all_trades_history', []):
                source = {'일반 매매': 'molit_apt', '분양권·입주권': 'molit_rights'}.get(t.get('type'))
                key = (str(group['complex']['id']), t['date'], str(Decimal(str(t['exclusive_area_exact'])).normalize()), int(t['price']), t.get('floor'), source)
                if key not in valid:
                    raise ValueError('Displayed transaction is absent from verified official source')


def require_current_source(groups, official):
    from datetime import datetime, timezone, timedelta
    stamp = datetime.fromisoformat(official['fetched_at'].replace('Z', '+00:00'))
    age = (datetime.now(timezone.utc)-stamp).total_seconds()
    if not 0 <= age <= 36*3600:
        raise ValueError('Official source older than 36 hours; generation blocked')
    if any(g.get('official_observed_at') != official['fetched_at'] for g in groups):
        raise ValueError('Website data and official source observations differ')
    validate_groups(groups, official)
