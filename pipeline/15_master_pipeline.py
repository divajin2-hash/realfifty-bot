import sys
import io
import time
import re
import xml.etree.ElementTree as ET
import urllib.request as request
import urllib.parse as parse
import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY") # 10년치 국토부 키

# 가격 문자열 int 변환 (네이버)
def parse_price(price_str):
    clean_str = price_str.replace(" ", "").replace(",", "").replace("\n", "").replace("만", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        digits_only = re.sub(r'[^0-9]', '', parts[1])
        man = int(digits_only) * 10000 if digits_only else 0
        return eok + man
    return 0

# (1) 단지별 메타데이터 동적 추출 (하드코딩 제거!)
def get_complex_pyeong_meta(page, complex_no):
    # 페이지를 통하여 직접 네이버 API JSON에 접근 (SSL 및 크롤링 차단 우회)
    api_url = f"https://new.land.naver.com/api/complexes/{complex_no}"
    try:
        page.goto(api_url)
        # JSON 텍스트 추출
        json_text = page.locator("pre").inner_text()
        import json
        data = json.loads(json_text)
        
        pyeongs = []
        for pyeong in data.get("complexPyeongDetailList", []):
            ptpNo = pyeong.get("ptpNo")
            pyeongNm = pyeong.get("pyeongNm")
            exclusive = pyeong.get("exclusiveArea")
            if not ptpNo or not exclusive: continue
            
            # 매칭 키: 전용면적 정수부분
            match_key = int(float(exclusive))
            
            # 중복 매칭 키 제거 (예: 84.9와 84.5가 있으면 하나로 통폐합)
            if not any(p["match_key"] == match_key for p in pyeongs):
                pyeongs.append({
                    "ptpNo": ptpNo,
                    "pyeongNm": pyeongNm,
                    "match_key": match_key,
                    "exclusive_exact": exclusive
                })
        return pyeongs
    except Exception as e:
        print(f"메타데이터 추출 실패: {e}")
        return []

# (2) 동적 추출된 평형(ptpNo)으로 즉각 네이버 호가 추출
def get_naver_ask(page, complex_no, ptpNo, match_key):
    url = f"https://new.land.naver.com/complexes/{complex_no}?a=APT&b=A1&ptpNo={ptpNo}&prcSort=asc"
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_selector(".item_inner", timeout=10000)
        
        # 기획자님 핵심: 동일매물 묶기
        try: page.locator("label:has-text('동일매물 묶기')").click(timeout=2000)
        except: pass
        
        time.sleep(1) # UI 업데이트 대기
        
        cards = page.locator(".item_inner").all()[:5]
        for card in cards:
            text = card.inner_text().replace('\n', ' ')
            if "지분" in text or "경매" in text:
                continue
            
            price_text = card.locator(".price").first.inner_text().strip()
            price_num = parse_price(price_text)
            
            # 강남권 20억 방어 필터 적용 여부 등 (임시 10억 적용)
            if price_num >= 1000000000:
                return price_num, price_text
        return None, None
    except:
        return None, None

def run_master():
    print("==================================================================")
    print("💎 [종합엔진] 하드코딩 제거 + 네이버 완벽 결합 파이프라인 가동 💎")
    print("==================================================================")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(user_agent="Mozilla/5.0")
        
        # Test 1: 대치은마 (8928) 만 집중 테스트
        complex_no = "8928"
        print("\n▶ 1. [대치은마] 평형 메타데이터 동적 추출 중...")
        pyeongs = get_complex_pyeong_meta(page, complex_no)
        
        for p_meta in pyeongs:
            print(f"   [평형 인식] 타겟: {p_meta['pyeongNm']} (전용 {p_meta['exclusive_exact']}㎡) -> 맵핑키: {p_meta['match_key']}")
            
            # 2. 호가 매핑
            price_num, price_txt = get_naver_ask(page, complex_no, p_meta["ptpNo"], p_meta["match_key"])
            if price_num:
                print(f"      ✅ 현재 최저호가 확보: {price_txt}")
            else:
                print(f"      ❌ 현재 매물 없음")
                
        browser.close()

if __name__ == "__main__":
    run_master()
