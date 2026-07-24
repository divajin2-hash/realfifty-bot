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

# 🔥 [프롭테크 표준] KB50 단지별 완벽한 전용면적(㎡) 타겟 사전을 정의합니다.
TARGET_MAPPING = {
    "111515": {"name": "송파 헬리오시티", "tab_20": 59, "tab_30": 84, "tab_40": 110},
    "1424": {"name": "서초 반포자이", "tab_20": 59, "tab_30": 84, "tab_40": 116},
    "10586": {"name": "마포 래미안푸르지오", "tab_20": 59, "tab_30": 84, "tab_40": 114},
    "27771": {"name": "잠실 엘스", "tab_20": 59, "tab_30": 84, "tab_40": 119},
    "95": {"name": "강남 대치은마", "tab_20": 76, "tab_30": 84, "tab_40": None}, # 은마는 전용 76이 제일 작음
}

def parse_korean_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        man = int(parts[1]) * 10000 if parts[1] else 0
        return eok + man
    return int(clean_str) * 10000

def get_clean_lowest_ask(context, complex_no, target_size, apt_name):
    # 면적 필터 없이 매매(A1) 낮은 가격순(prcSort=asc) 전체 조회
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&prcSort=asc"
    page = context.new_page()
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_selector(".item_inner", timeout=15000)
        
        # 목록을 넉넉하게 불러오기 위해 약간 스크롤
        for _ in range(5):
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(300)
            
        items = page.locator(".item_inner").all_inner_texts()
        
        # 필터링 로직: 허위매물/지분 배제하고 정확한 타겟 평수만 찾기
        for item_text in items:
            # 1. 지분, 경매, 보류지 등 허위/비정상 매물 텍스트가 있으면 무조건 패스
            if "지분" in item_text or "보류지" in item_text or "경매" in item_text:
                continue
                
            # 2. 전용면적 추출 (예: '33A/84㎡' -> 84)
            m = re.search(r'/([0-9\.]+)(㎡|m)', item_text)
            if not m:
                continue
                
            actual_area = float(m.group(1))
            
            # 3. 추출한 전용면적이 우리가 설정한 타겟(예: 84)과 맞는지 확인 (소수점 버림 일치)
            if int(actual_area) == int(target_size):
                # 완벽하게 일치하는 첫 번째 매물이 진짜 최저가!
                price_text = re.search(r'([0-9]+억\s*[0-9,]*)', item_text).group(1)
                numeric_price = parse_korean_price(price_text)
                print(f"   ✅ [정상 매물 포착] 전용 {actual_area}㎡ 👉 {price_text} ({numeric_price:,}원)")
                page.close()
                return numeric_price
                
        print(f"   ❌ 해당 평형({target_size}㎡)의 정상 매물이 현재 없습니다.")
        page.close()
        return None

    except Exception as e:
        print(f"   ⚠️ 크롤링 오류: {e}")
        page.close()
        return None

def run_master_pipeline():
    print("===============================================================")
    print("🔥 [Phase 4] 하드코딩 매핑 + 딥 필터링 호가 스크래퍼 가동 🔥")
    print("===============================================================")
    
    complexes = supabase.table("complexes").select("*").execute().data
    if not complexes: return
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        for c in complexes:
            complex_id = c["id"]
            complex_no = c["complex_no"]
            apt_name = c["name"]
            
            if complex_no not in TARGET_MAPPING:
                continue
                
            # 국민평형(tab_30)을 대표 분석 평형으로 설정
            target_size = TARGET_MAPPING[complex_no]["tab_30"]
            
            print(f"\n▶ 🏢 [{apt_name}] (목표: 전용 {target_size}㎡) 딥 스캔 중...")
            
            lowest_ask = get_clean_lowest_ask(context, complex_no, target_size, apt_name)
            
            if lowest_ask:
                # DB 업데이트
                existing = supabase.table("market_stats").select("id").eq("complex_id", complex_id).execute().data
                
                if existing:
                    supabase.table("market_stats").update({
                        "current_lowest_price": lowest_ask
                    }).eq("complex_id", complex_id).execute()
                else:
                    supabase.table("market_stats").insert({
                        "complex_id": complex_id,
                        "current_lowest_price": lowest_ask,
                        "mdd_rate": -15.0, # 더미
                        "highest_price": int(lowest_ask * 1.25)
                    }).execute()
                    
                print(f"   💾 Supabase 연동 완료!")
                
        browser.close()
    print("\n✅ 모든 단지 정상 호가 추출 완료!")

if __name__ == "__main__":
    run_master_pipeline()
