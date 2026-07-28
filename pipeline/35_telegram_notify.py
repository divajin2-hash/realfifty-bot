import os
import requests
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from supabase import create_client

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
    yesterday_date = (datetime.now(KST) - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"Fetching summary stats for {today_date} vs {yesterday_date}...")
    
    # Query Supabase
    res_today = supabase.table('daily_history').select('*').eq('base_date', today_date).execute()
    res_yest = supabase.table('daily_history').select('*').eq('base_date', yesterday_date).execute()
    
    if not res_today.data:
        print("No daily history data found for today.")
        return
        
    yest_dict = {(r['complex_id'], r['area']): r for r in res_yest.data}
    
    ask_drops = []
    recent_updates = []
    
    for t in res_today.data:
        key = (t['complex_id'], t['area'])
        y = yest_dict.get(key)
        if not y:
            continue
            
        c_name = t['complex_name']
        area = t['area']
        
        # Check asking price drop
        if t['lowest_ask'] and y['lowest_ask'] and t['lowest_ask'] < y['lowest_ask']:
            diff = y['lowest_ask'] - t['lowest_ask']
            ask_drops.append(f"- {c_name} {area}㎡: {y['lowest_ask']//10000}만 📉 {t['lowest_ask']//10000}만 (▼{diff//10000}만)")
            
        # Check new recent deals
        if t['recent_price'] and y['recent_price'] and t['recent_price'] != y['recent_price']:
            diff = t['recent_price'] - y['recent_price']
            mark = "🔺" if diff > 0 else "🔻"
            recent_updates.append(f"- {c_name} {area}㎡: {y['recent_price']//10000}만 ➡️ {t['recent_price']//10000}만 ({mark}{abs(diff)//10000}만)")
            
    # Format message
    msg = f"🔔 *RealFifty 데일리 업데이트 완료!*\n({today_date} 자정 기준)\n\n"
    msg += f"✅ 국토부 실거래가 및 네이버 호가 50개 단지 수집 및 DB 저장 완료.\n\n"
    
    if ask_drops:
        msg += "📉 *주요 24시간 호가 하락*\n" + "\n".join(ask_drops[:10]) + "\n"
        if len(ask_drops) > 10:
            msg += f"...외 {len(ask_drops)-10}건 더 있음\n"
        msg += "\n"
        
    if recent_updates:
        msg += "💸 *새로운 실거래가 업데이트*\n" + "\n".join(recent_updates[:10]) + "\n"
        if len(recent_updates) > 10:
            msg += f"...외 {len(recent_updates)-10}건 더 있음\n"
        msg += "\n"
        
    if not ask_drops and not recent_updates:
        msg += "평온한 하루네요. 오늘 감지된 특이 변동사항(호가 하락 및 신규 실거래)이 없습니다."
        
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
