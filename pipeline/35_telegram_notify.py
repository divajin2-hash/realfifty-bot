import os
import json
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

def format_price(price):
    if price == 0:
        return "0원"
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
    
    KST = timezone(timedelta(hours=9))
    today_date = datetime.now(KST).strftime('%Y-%m-%d')
    res_dates = supabase.table('daily_history').select('base_date').lt('base_date', today_date).order('base_date', desc=True).limit(1).execute()
    if res_dates.data:
        prev_date = res_dates.data[0]['base_date']
    else:
        prev_date = (datetime.now(KST) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"Fetching summary stats for {today_date} vs {prev_date}...")
    
    res_today = supabase.table('daily_history').select('*').eq('base_date', today_date).execute()
    res_yest = supabase.table('daily_history').select('*').eq('base_date', prev_date).execute()
    
    if not res_today.data:
        print("No daily history data found for today.")
        return
        
    yest_dict = {(r['complex_id'], r['area']): r for r in res_yest.data}

    # Load pyeong_name map from kb50_stats.json: (complex_id, match_key_area) -> pyeong_name
    pyeong_name_map = {}
    try:
        stats_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'src', 'data', 'kb50_stats.json')
        kb50 = json.load(open(stats_path, encoding='utf-8'))
        for cx in kb50:
            cx_id = cx['complex'].get('id')
            for s in cx.get('stats', []):
                area = s.get('match_key_area')
                pname = s.get('pyeong_name')
                if cx_id and area and pname:
                    pyeong_name_map[(cx_id, area)] = pname
    except Exception as e:
        print(f"Warning: could not load pyeong_name map: {e}")
    
    # Lists to hold formatted strings
    rtms_changes = []
    ask_changes = []
    
    for t in res_today.data:
        key = (t['complex_id'], t['area'])
        y = yest_dict.get(key)
        if not y:
            continue
            
        c_name = t['complex_name']
        area = t['area']
        
        # 1. 국토부 실거래가 (recent_price 변동 비교)
        t_recent = t.get('recent_price') or 0
        y_recent = y.get('recent_price') or 0
        if t_recent > 0 and y_recent > 0 and t_recent != y_recent:
            diff = t_recent - y_recent
            diff_abs = abs(diff)
            mark = "🔺상승" if diff > 0 else "🔻하락"
            
            t_str = format_price(t_recent)
            y_str = format_price(y_recent)
            d_str = format_price(diff_abs)
            
            rtms_changes.append(f"- {c_name} {area}㎡: {y_str} ➡️ {t_str} ({mark} {d_str})")
            
            # Use type-specific breakdown
            pname = pyeong_name_map.get((t.get('complex_id'), area))
            if pname and pname != str(area):
                rtms_changes[-1] = rtms_changes[-1].replace(f"{c_name} {area}㎡:", f"{c_name} {pname}({area}㎡):")
            
        # 2. 네이버 최저호가 (lowest_ask 변동 비교)
        t_ask = t.get('lowest_ask') or 0
        y_ask = y.get('lowest_ask') or 0
        
        if t_ask > 0 and y_ask > 0 and t_ask != y_ask:
            diff = t_ask - y_ask
            diff_abs = abs(diff)
            mark = "📈상승" if diff > 0 else "📉하락"
            
            t_str = format_price(t_ask)
            y_str = format_price(y_ask)
            d_str = format_price(diff_abs)
            
            ask_changes.append(f"- {c_name} {area}㎡: {y_str} ➡️ {t_str} ({mark} {d_str})") 

            # 2b. Also show type-specific breakdown using pyeong_name
            pname = pyeong_name_map.get((t.get('complex_id'), area))
            if pname and pname != str(area):  # Only add suffix if it adds info (e.g. "84A" not just "84")
                ask_changes[-1] = ask_changes[-1].replace(f"{c_name} {area}㎡:", f"{c_name} {pname}({area}㎡):")
            
    # Format message
    msg = f"🔔 *RealFifty 데일리 리포트*\n({today_date} 자정 기준)\n\n"
    
    msg += f"🏢 *1. 국토부 실거래가 신규 등록* : 총 {len(rtms_changes)}건\n"
    if rtms_changes:
        msg += "\n".join(rtms_changes[:15]) + "\n"
        if len(rtms_changes) > 15:
            msg += f"...외 {len(rtms_changes)-15}건 더 있음\n"
    else:
        msg += "새롭게 등록된 실거래가 변동 내역이 없습니다.\n"
    
    msg += "\n"
    msg += f"🏷️ *2. 네이버 최저호가 변동* : 총 {len(ask_changes)}건\n"
    if ask_changes:
        msg += "\n".join(ask_changes[:15]) + "\n"
        if len(ask_changes) > 15:
            msg += f"...외 {len(ask_changes)-15}건 더 있음\n"
    else:
        msg += f"{prev_date} 대비 최저호가 변동 내역이 없습니다.\n"
        
    # Send
    t_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    r = requests.post(t_url, json=payload)
    if r.status_code != 200:
        print(f"Failed to send telegram message: {r.text}")
    else:
        print("Telegram notification sent successfully!")

if __name__ == "__main__":
    run()
