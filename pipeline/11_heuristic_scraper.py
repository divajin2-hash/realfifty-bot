import os
import sys
import io
import time
import re
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 더미 삭제 완료된 진실의 방 매핑
FULL_TARGET_MAPPING = {
    "111515": {"name": "송파 헬리오시티", "pyeongs": [39, 49, 59, 84, 110, 130, 150]},
    "25096": {"name": "서초 반포자이", "pyeongs": [59, 84, 116, 132, 165, 194, 216, 244]},
    "100438": {"name": "마포 래미안푸르지오", "pyeongs": [59, 84, 114]},
    "27771": {"name": "잠실 엘스", "pyeongs": [59, 84, 119]},
    "95": {"name": "강남 대치은마", "pyeongs": [76, 84]},
}

def parse_korean_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        digits_only = re.sub(r'[^0-9]', '', parts[1])
        man = int(digits_only) * 10000 if digits_only else 0
        return eok + man
    digits_only = re.sub(r'[^0-9]', '', clean_str)
    return int(digits_only) * 10000 if digits_only else 0

def get_all_lowest_asks(context, complex_no, target_pyeongs):
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&prcSort=asc"
    page = context.new_page()
    results = {}
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_selector(".item_inner", timeout=15000)
        
        for _ in range(15):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(300)
            
        cards = page.locator(".item_inner").all()
        
        bucket = {}
        for card in cards:
            text = card.inner_text()
            
            if "지분" in text or "보류지" in text or "경매" in text:
                continue
                
            area_match = re.search(r'/([0-9\.]+)(㎡|m)', text)
            if not area_match: continue
            area_key = int(float(area_match.group(1)))
            
            try:
                price_text = card.locator(".price").first.inner_text().strip()
                price_num = parse_korean_price(price_text)
            except Exception:
                continue
            
            # 🔥 핵심 휴리스틱 방어: 강남권 및 전국 50대장주에서 매매가가 7억 이하면 "무조건" 갭투자금/지분 어그로 가짜매물임
            if area_key not in bucket and price_num > 700000000:
                bucket[area_key] = price_num
                
        for target in target_pyeongs:
            if target in bucket:
                results[target] = bucket[target]
                
        page.close()
        return results

    except Exception as e:
        page.close()
        return {}

def run():
    print("==================================================================")
    print("💎 [진실의 방] 미끼 매물 완벽 제거된 순수 대장주 최저가 시세 💎")
    print("==================================================================")
    
    with sync_playwright() as p:
        # Run headlessly in CI (like Github Actions) by checking env var
        is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
        browser = p.chromium.launch(headless=is_ci, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        for complex_no, meta in FULL_TARGET_MAPPING.items():
            print(f"\n▶ 🏢 [{meta['name']}] (어그로/갭투자 미끼 매물 배제 스캔 중...)")
            target_sizes = meta["pyeongs"]
            
            all_lowest_asks = get_all_lowest_asks(context, complex_no, target_sizes)
            
            for pyeong in sorted(all_lowest_asks.keys()):
                price = all_lowest_asks[pyeong]
                eok = price // 100000000
                man = (price % 100000000) // 10000
                display_price = f"{eok}억 {man}만" if man else f"{eok}억"
                print(f"   ✅ [전용 {pyeong}㎡ 그룹] 진짜 실매물 최저가 👉 {display_price} ({price:,}원)")
                
        browser.close()

if __name__ == "__main__":
    run()
