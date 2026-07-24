import os
import sys
import io
import time
import re
from dotenv import load_dotenv
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

# 🔥 드디어 수정된 진짜 찐단지 번호 매핑! (더미 삭제 완료)
FULL_TARGET_MAPPING = {
    "111515": {"name": "송파 헬리오시티", "pyeongs": [39, 49, 59, 84, 110, 130, 150]},
    "25096": {"name": "서초 반포자이", "pyeongs": [59, 84, 116, 132, 165, 194, 216, 244]}, # 진짜 반포자이
    "100438": {"name": "마포 래미안푸르지오", "pyeongs": [59, 84, 114]}, # 진짜 마래푸
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
            except Exception as e:
                continue
            
            if area_key not in bucket and price_num > 100000000:
                bucket[area_key] = price_num
                
        for target in target_pyeongs:
            if target in bucket:
                results[target] = bucket[target]
                
        page.close()
        return results

    except Exception as e:
        print(f"   ⚠️ 크롤링 오류: {e}")
        page.close()
        return {}

def run_master():
    print("==================================================================")
    print("🔥 [드디어 진실의 방] 진짜 서울 대장주 다중 평형 수집 봇 가동! 🔥")
    print("==================================================================")
    
    # 📌 우선 Supabase에서 1424, 10586 등 옛날 테스트용 짭 데이터 방어를 위한 쿼리 가져오기
    complexes = supabase.table("complexes").select("*").in_("complex_no", list(FULL_TARGET_MAPPING.keys())).execute().data
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        for c in complexes:
            complex_id = c["id"]
            complex_no = c["complex_no"]
            apt_name = FULL_TARGET_MAPPING[complex_no]["name"]
            target_sizes = FULL_TARGET_MAPPING[complex_no]["pyeongs"]
            
            print(f"\n▶ 🏢 [{apt_name}] 진입 중... (진짜 강남/강남권 데이터 긁어오는 중)")
            all_lowest_asks = get_all_lowest_asks(context, complex_no, target_sizes)
            
            if not all_lowest_asks:
                print("   ❌ 호가 수집 실패 (로딩 지연 등)")
                continue
                
            for pyeong in sorted(all_lowest_asks.keys()):
                price = all_lowest_asks[pyeong]
                eok = price // 100000000
                man = (price % 100000000) // 10000
                display_price = f"{eok}억 {man}만" if man else f"{eok}억"
                print(f"   ✅ [전용 {pyeong}㎡ 그룹] 찐최저가 👉 {display_price} ({price:,}원)")
                
        browser.close()
    print("\n✅ 놀라운 진짜 시세 검증 완료!")

if __name__ == "__main__":
    run_master()
