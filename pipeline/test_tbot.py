import os
import requests
from dotenv import load_dotenv
from supabase import create_client

def format_price(price):
    if price == 0: return "0원"
    eok = price // 100000000
    man = (price % 100000000) // 10000
    res = ""
    if eok > 0: res += f"{eok}억"
    if man > 0: res += f"{man}만" if eok == 0 else f" {man}만"
    return res

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

rtms_changes = [
    f"- 잠실 엘스 84㎡: {format_price(2200000000)} ➡️ {format_price(2350000000)} (🔺상승 {format_price(150000000)})",
    f"- 래미안 원베일리 59㎡: {format_price(2900000000)} ➡️ {format_price(2950000000)} (🔺상승 {format_price(50000000)})"
]

ask_changes = [
    f"- 아크로 리버파크 84㎡: {format_price(4300000000)} ➡️ {format_price(4200000000)} (📉하락 {format_price(100000000)})",
    f"- 헬리오시티 59㎡: {format_price(1680000000)} ➡️ {format_price(1650000000)} (📉하락 {format_price(30000000)})",
    f"- 신동아 110㎡: {format_price(2100000000)} ➡️ {format_price(2150000000)} (📈상승 {format_price(50000000)})"
]

msg = f"🔔 *RealFifty 데일리 리포트 (시뮬레이션 예시)*\n\n"
msg += f"🏢 *1. 국토부 실거래가 신규 등록* : 총 {len(rtms_changes)}건\n"
msg += "\n".join(rtms_changes) + "\n\n"
msg += f"🏷️ *2. 네이버 최저호가 변동* : 총 {len(ask_changes)}건\n"
msg += "\n".join(ask_changes) + "\n"

t_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
requests.post(t_url, json=payload)
print("Demo sent!")
