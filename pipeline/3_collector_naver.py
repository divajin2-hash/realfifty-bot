import os
import sys
import io
import time
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

if not URL or not KEY:
    print("❗ 에러: .env 파일에 SUPABASE 접속 정보가 없습니다.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

def parse_korean_price(price_str):
    # 예: "18억 5,000", "20억", "9,500"
    clean_str = price_str.replace(" ", "").replace(",", "")
    if "억" in clean_str:
        parts = clean_str.split("억")
        eok = int(parts[0]) * 100000000
        man = int(parts[1]) * 10000 if parts[1] else 0
        return eok + man
    else:
        return int(clean_str) * 10000

def fetch_naver_lowest_price(page, complex_no):
    # a=APT(아파트), b=A1(매매), prcSort=asc(낮은 가격순 정렬)
    # 84㎡ 국민평형(공급 105~115㎡)을 필터링하기 위해 spcMin=105 & spcMax=115 파라미터를 명시합니다.
    url = f"https://new.land.naver.com/complexes/{complex_no}?ms=37.495,127.1,15&a=APT&b=A1&spcMin=105&spcMax=115&rtype=a&prcSort=asc"
    
    try:
        page.goto(url, timeout=30000)
        
        # 좌측 리스트에 매물 가격('.price' 태그)이 뜰 때까지 기다립니다.
        page.wait_for_selector(".price", timeout=10000)
        
        # 첫 번째 매물의 가격 텍스트 가져오기 (예: "18억 5,000")
        price_text = page.locator(".price").first.inner_text().strip()
        
        # 상세 정보 텍스트 가져오기 (동/호수/면적 등)
        try:
            info_text = page.locator(".item_inner").first.inner_text().replace('\n', ' / ')[:70]
        except:
            info_text = "상세 정보 파싱 불가"
        
        return {
            "raw_price": price_text,
            "numeric_price": parse_korean_price(price_text),
            "source_url": url,
            "item_name": info_text
        }
        
    except Exception as e:
        print(f"화면 크롤링 에러 (대기 시간 초과 또는 캡차): {e}")
        return None

def run_naver_crawler():
    print("🚀 [국민평형 84㎡ 중심] 네이버 부동산 최저 호가 수집 및 DB 저장 시작...")
    
    complexes_data = supabase.table("complexes").select("*").execute().data
    if not complexes_data:
        print("DB에 저장된 아파트 단지가 없습니다.")
        return

    # 눈에 보이게 크롬 창을 띄워서 네이버 봇 탐지를 회피합니다 (headless=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        # navigator.webdriver 우회 스크립트 주입
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        for c in complexes_data:
            complex_no = c.get("complex_no")
            complex_id = c.get("id")
            apt_name = c.get("name")
            
            if not complex_no:
                continue
                
            print(f"\n📡 [{apt_name}] 국민평형(84㎡) 최저 호가 탐색 중...")
            
            result = fetch_naver_lowest_price(page, complex_no)
            
            if result:
                price_str = result['raw_price']
                price_num = result['numeric_price']
                url = result['source_url']
                info = result['item_name']
                print(f"   [🚨 매물 발견] {info} 👉 {price_str} ({price_num}원)")
                
                # DB (listings 테이블)에 데이터 삽입
                try:
                    supabase.table("listings").insert({
                        "complex_id": complex_id,
                        "price": price_num,
                        "is_bargain": False,
                        "source_url": url
                    }).execute()
                    print(f"   ✅ DB 저장 완료!")
                except Exception as db_err:
                    print(f"   ❌ DB 저장 중 에러 발생: {db_err}")
                
            else:
                print(f"   🤔 현재 조건에 맞는 매매 호가 매물이 없습니다.")
        
        browser.close()
            
    print("\n✅ 모든 호가 수집 및 탐색이 완료되었습니다!")

if __name__ == "__main__":
    run_naver_crawler()
