import os
import json
import requests
from datetime import datetime, timedelta, timezone as dt_timezone
from dotenv import load_dotenv
from supabase import create_client

def format_price(price):
    if price == 0:
        return "0"
    eok = price // 100000000
    man = (price % 100000000) // 10000
    res = ""
    if eok > 0:
        res += f"{eok}억"
    if man > 0:
        res += f"{man}만" if eok == 0 else f" {man}만"
    return res

def run():
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
    
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram bot token or chat ID not set. Skipping notification.")
        return
        
    URL = os.environ.get("SUPABASE_URL")
    KEY = os.environ.get("SUPABASE_KEY")
    supabase = create_client(URL, KEY)
    
    KST = dt_timezone(timedelta(hours=9))
    today_date = datetime.now(KST).strftime('%Y-%m-%d')
    res_dates = supabase.table('daily_history').select('base_date').lt('base_date', today_date).order('base_date', desc=True).limit(1).execute()
    if res_dates.data:
        prev_date = res_dates.data[0]['base_date']
    else:
        prev_date = (datetime.now(KST) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    res_today = supabase.table('daily_history').select('*').eq('base_date', today_date).execute()
    res_yest = supabase.table('daily_history').select('*').eq('base_date', prev_date).execute()
    
    if not res_today.data:
        return
        
    yest_dict = {(r['complex_id'], r['area']): r for r in res_yest.data}

    pyeong_name_map = {}
    try:
        stats_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'kb50_stats.json')
        kb50 = json.load(open(stats_path, encoding='utf-8'))
        for cx in kb50:
            cid = cx.get('complex', {}).get('id')
            for item in cx.get('stats', []):
                pyeong_name_map[(cid, item.get('match_key_area'))] = item.get('pyeong_name')
    except Exception as e:
        print(f"Warning: could not load pyeong_name map: {e}")
    
    rtms_rises = []
    rtms_falls = []
    ask_rises = []
    ask_falls = []
    
    rtms_rise_diffs = []
    rtms_fall_diffs = []
    ask_rise_diffs = []
    ask_fall_diffs = []
    
    for t in res_today.data:
        key = (t['complex_id'], t['area'])
        y = yest_dict.get(key)
        if not y:
            continue
            
        c_name = t['complex_name']
        area = t['area']
        pname = pyeong_name_map.get((t.get('complex_id'), area), str(area))
        name_str = f"{c_name} {pname}({area}㎡):" if pname != str(area) else f"{c_name} {area}㎡:"
        
        # 1. RTMS
        t_recent = t.get('recent_price') or 0
        y_recent = y.get('recent_price') or 0
        if t_recent > 0 and y_recent > 0 and t_recent != y_recent:
            diff = t_recent - y_recent
            diff_abs = abs(diff)
            t_str = format_price(t_recent)
            y_str = format_price(y_recent)
            d_str = format_price(diff_abs)
            
            s = f"- {name_str} {y_str} ➡️ {t_str} "
            if diff > 0:
                s += f"(🔺상승 {d_str})"
                rtms_rises.append(s)
                rtms_rise_diffs.append(diff)
            else:
                s += f"(🔻하락 {d_str})"
                rtms_falls.append(s)
                rtms_fall_diffs.append(diff_abs)
            
        # 2. Asks
        t_ask = t.get('lowest_ask') or 0
        y_ask = y.get('lowest_ask') or 0
        if t_ask > 0 and y_ask > 0 and t_ask != y_ask:
            diff = t_ask - y_ask
            diff_abs = abs(diff)
            t_str = format_price(t_ask)
            y_str = format_price(y_ask)
            d_str = format_price(diff_abs)
            
            s = f"- {name_str} {y_str} ➡️ {t_str} "
            if diff > 0:
                s += f"(📈상승 {d_str})"
                ask_rises.append(s)
                ask_rise_diffs.append(diff)
            else:
                s += f"(📉하락 {d_str})"
                ask_falls.append(s)
                ask_fall_diffs.append(diff_abs)
            
    def _build_section(rises, falls, rise_diffs, fall_diffs, limit=15):
        s = ""
        total_len = len(rises) + len(falls)
        if total_len == 0:
            return ""
            
        if rises:
            avg_rt = sum(rise_diffs) // len(rise_diffs) if rise_diffs else 0
            s += f"[⬆️상승 {len(rises)}건]\n"
            s += "\n".join(rises[:limit]) + "\n"
            if len(rises) > limit:
                s += f"...가독성을 위해 {len(rises)-limit}건 생략\n"
            s += "\n"
        
        if falls:
            avg_ft = sum(fall_diffs) // len(fall_diffs) if fall_diffs else 0
            s += f"[⬇️하락 {len(falls)}건]\n"
            s += "\n".join(falls[:limit]) + "\n"
            if len(falls) > limit:
                s += f"...가독성을 위해 {len(falls)-limit}건 생략\n"
            s += "\n"
        return s

    msg = f"🔔 *RealFifty 데일리 리포트*\n({today_date} 수집분 기준)\n\n"
    
    rtms_total = len(rtms_rises) + len(rtms_falls)
    msg += f"🏢 *1. 최근 실거래 가격이 달라진 면적 그룹* : 총 {rtms_total}건\n"
    if rtms_total > 0:
        msg += _build_section(rtms_rises, rtms_falls, rtms_rise_diffs, rtms_fall_diffs, 10)
    else:
        msg += "최근 실거래 가격이 달라진 면적 그룹이 없습니다.\n\n"
        
    ask_total = len(ask_rises) + len(ask_falls)
    msg += f"🏷️ *2. 대표 타입 최저호가 변동* : 총 {ask_total}건\n"
    if ask_total > 0:
        msg += _build_section(ask_rises, ask_falls, ask_rise_diffs, ask_fall_diffs, 15)
    else:
        msg += f"{prev_date} 대비 최저호가 변동 내역이 없습니다.\n"
        
    msg += "\n※ 신규 계약 건수가 아닌 일별 대표 가격 비교입니다. 같은 정수 면적의 타입을 묶은 집계로 웹의 타입별 집계와 다릅니다. 최저호가 변화는 동일 매물의 가격 수정과 다를 수 있습니다.\n"
    t_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    r = requests.post(t_url, json=payload)
    if r.status_code != 200:
        print("Failed to send telegram msg:", r.text)
    else:
        print("Telegram notification sent successfully!")

if __name__ == '__main__':
    run()
