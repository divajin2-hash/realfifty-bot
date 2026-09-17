"""Conservative area-based candidate matching; never infer a floor-plan code."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path
from functools import lru_cache

def area_key(value):
    try:
        v=Decimal(str(value))
        if not v.is_finite() or v<=0:return None
        return v.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)
    except (InvalidOperation,ValueError,TypeError):return None

def trade_key(trade):
    return '|'.join(str(v) for v in (trade['deal_date'], trade['deal_price'], trade.get('floor'), trade.get('source'), Decimal(str(trade['exclusive_area_exact'])).normalize()))

@lru_cache(maxsize=1)
def load_evidence():
    path = Path(__file__).with_name('type_trade_evidence.json')
    return json.loads(path.read_text(encoding='utf-8')).get('types', {}) if path.exists() else {}

def match_trades(ask, asks, trades):
    key=area_key(ask.get('exclusive_area'))
    peers={(str(a.get('naver_complex_no')),str(a.get('ptp_no'))) for a in asks if key is not None and area_key(a.get('exclusive_area'))==key}
    entry=load_evidence().get(f"{ask.get('naver_complex_no')}:{ask.get('ptp_no')}", {})
    evidence=set(entry.get('trade_keys', [])) if area_key(entry.get('asking_area'))==key else set()
    exact=[];crosschecked=0
    for t in trades:
        raw_area=t.get('exclusive_area_exact')
        if area_key(raw_area) is None:continue
        area_matches=key is not None and area_key(raw_area)==key
        proven=trade_key(t) in evidence
        if area_matches or proven:
            exact.append(t)
            if proven and not area_matches:crosschecked+=1
    missing=sum(area_key(t.get('exclusive_area_exact')) is None for t in trades)
    status=('shared_area' if len(peers)>1 else 'area_matched') if exact else 'unmatched'
    return exact, {'status':status,'basis':'transaction_crosscheck' if crosschecked else 'exclusive_area_2dp','crosschecked_trade_count':crosschecked,'candidate_types':len(peers),'reference_trade_count':len(exact),'excluded_missing_area':missing}
