"""Notify from official observations and the exact type-level web comparison."""
import json
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone
import requests
from dotenv import load_dotenv
from official_changes import digest
ROOT = Path(__file__).resolve().parents[1]

def format_price(price):
    eok, man = divmod(int(price)//10000, 10000)
    return (f"{eok}억 " if eok else '') + (f"{man}만" if man else '') or '0'

def build_message(official, asks, today):
    if asks.get('date') != today or asks.get('unavailable'):
        raise ValueError('Current type-level asking comparison unavailable')
    observed = datetime.fromisoformat(official['fetched_at']).astimezone(timezone(timedelta(hours=9))).date().isoformat()
    if observed != today:
        raise ValueError('Official source is not refreshed today')
    changes = official.get('observation_changes', {})
    if changes.get('source_digest') != digest(official):
        raise ValueError('Official comparison does not match source')
    lines = [f'🔔 RealFifty 데일리 리포트 ({today} 수집분)', '', '🏢 1. 국토부 원본 거래 목록 대조']
    if changes.get('status') == 'compared':
        lines += [f"이전 수집 대비 추가 관측 {changes['added']}건 / 목록 제외 {changes['removed']}건",
                  '추가 관측은 과거 계약의 지연 신고·정정을 포함할 수 있습니다. 목록 제외는 해제·정정 등의 재확인 대상이며 신규 계약·가격 상승·하락 건수로 집계하지 않습니다.']
    else:
        lines += ['비교 기준 자료 설정 중 — 신규 거래 건수 집계를 보류합니다.']
    lines += ['', f"🏷 2. 타입별 최저호가 변화 ({asks['previousDate']} → {today})",
              f"비교 가능 {asks['comparable']}개 타입 · 상승 {asks['rises']} · 하락 {asks['falls']} · 동일 {asks['unchanged']}"]
    for label, predicate in [('↑ 상승',lambda r:r['after']>r['before']),('↓ 하락',lambda r:r['after']<r['before'])]:
        rows=[r for r in asks['rows'] if predicate(r)]
        lines += ['', label]
        for r in rows[:8]:
            lines.append(f"- {r['name']} {r['label']}: {format_price(r['before'])} → {format_price(r['after'])}")
        if len(rows)>8: lines.append(f'외 {len(rows)-8}개 타입 — 전체 목록은 웹에서 확인')
    lines += ['', f"호가 새로 확인 {asks['appeared']}개 · 호가 사라짐 {asks['disappeared']}개 · 비교 제외 {asks['missing']}개",
              '※ 웹과 동일한 타입별 집계입니다. 최저호가 변화는 동일 매물의 가격 수정이나 실제 체결 가격 변화와 다릅니다.']
    return '\n'.join(lines)

def run():
    load_dotenv(ROOT/'pipeline/.env')
    today=datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    official=json.loads((ROOT/'pipeline/rtms_recheck/verified_full.json').read_text(encoding='utf-8'))
    asks=json.loads((ROOT/'web/src/data/daily_changes.json').read_text(encoding='utf-8'))
    message=build_message(official,asks,today)
    if not os.environ.get('TELEGRAM_BOT_TOKEN') or not os.environ.get('TELEGRAM_CHAT_ID'):
        print('Telegram credentials unavailable; notification skipped')
        return
    response=requests.post('https://api.telegram.org/bot'+os.environ['TELEGRAM_BOT_TOKEN']+'/sendMessage',
                           json={'chat_id':os.environ['TELEGRAM_CHAT_ID'],'text':message},timeout=30)
    if response.status_code!=200 or not response.json().get('ok'):
        raise RuntimeError('Telegram delivery failed')
    print('Telegram notification sent')

if __name__ == '__main__':
    run()
