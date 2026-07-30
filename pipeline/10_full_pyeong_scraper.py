import os
import sys
import io
import time
import re
import json
from datetime import datetime
from playwright.sync_api import sync_playwright

from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

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

def run_master():
    print("==================================================================")
    print("🔥 [원자 단위] 서울 대장주 50단지 개별 평형별 최저호가 수집 봇 가동! 🔥")
    print("==================================================================")
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    output_filename = f"raw_daily_asks_{today_str}.json"
    
    all_results = []
    
    mapping_path = os.path.join(os.path.dirname(__file__), "naver_complex_mapping.json")
    try:
        with open(mapping_path, "r", encoding="utf-8") as mf:
            naver_mapping = json.load(mf)
    except Exception:
        print("❌ 네이버 매핑 파일(naver_complex_mapping.json)이 없습니다. 매퍼를 먼저 실행하세요.")
        return

    print("📌 DB에서 타겟 단지 목록 50개 로드 중...")
    complexes_data = supabase.table("complexes").select("*").execute().data
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        main_page = context.new_page()

        for c_meta in complexes_data:
            complex_no_db = str(c_meta["complex_no"])
            apt_name = c_meta["name"]
            
            naver_ids = naver_mapping.get(complex_no_db)
            if not naver_ids:
                print(f"\n⚠️ [{apt_name}] 네이버 매핑 ID가 없어 건너뜁니다.")
                continue
                
            if isinstance(naver_ids, str):
                naver_ids = [naver_ids]
                
            print(f"\n▶ 🏢 [{apt_name}] 평형 리스트 추출 (API 감청)... (총 {len(naver_ids)}개 네이버 단지 통합)")
            
            combined_ptps = []
            
            for nid in naver_ids:
                found_api_url = None
                target_ptp_info = None

                def handle_response(response):
                    nonlocal found_api_url, target_ptp_info
                    if found_api_url: return
                    url = response.url
                    if "complex" in url.lower() or "overview" in url.lower():
                        try:
                            data = response.json()
                            data_str = str(data)
                            if "pyeongs" in data_str or "complexPyeongDetailList" in data_str:
                                found_api_url = url
                                target_ptp_info = data
                        except:
                            pass

                main_page.on("response", handle_response)
                main_url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1"
                
                try:
                    main_page.goto(main_url, wait_until='networkidle', timeout=12000)
                except:
                    pass
                    
                main_page.wait_for_timeout(1500)
                main_page.remove_listener("response", handle_response)
                
                if target_ptp_info:
                    ptps = []
                    if "pyeongs" in target_ptp_info:
                        ptps = target_ptp_info["pyeongs"]
                    elif "result" in target_ptp_info and "complexDetail" in target_ptp_info["result"]:
                        ptps = target_ptp_info["result"]["complexDetail"].get("complexPyeongDetailList", [])
                    elif "complexPyeongDetailList" in target_ptp_info:
                        ptps = target_ptp_info["complexPyeongDetailList"]
                        
                    for p in ptps:
                        p['_naver_id'] = nid
                    combined_ptps.extend(ptps)
                else:
                    print(f"   ❌ 단지 {apt_name}({nid}) API 감청 실패")

            if not combined_ptps:
                print(f"   ❌ 단지 {apt_name} 전체 평형 정보 확보 실패")
                continue
                
            print(f"   ✅ 총 {len(combined_ptps)}개 타입 확보 완료. 개별 수집 시작!")
            failed_queue = []
            
            def process_ptp(p_type, retry_count=0):
                ptp_no = p_type.get('pyeongNo') or p_type.get('ptpNo')
                ptp_nm = p_type.get('pyeongName') or p_type.get('pyeongNm')
                ex_area = float(p_type.get('exclusiveArea', 0))
                sup_area = float(p_type.get('supplyArea') or p_type.get('supplySpace') or 0)
                nid = p_type.get('_naver_id')
                
                target_url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1&ptpNo={ptp_no}"
                
                target_page = context.new_page()
                try:
                    target_page.goto(target_url, wait_until="networkidle", timeout=12000)
                    
                    try:
                        target_page.wait_for_selector(".item_inner", timeout=4000)
                    except:
                        print(f"   [{ptp_nm:<7} / 전용 {ex_area:>5}] -> 매물없음")
                        return True
                    
                    import time
                    time.sleep(0.5)
                    
                    price_btn = target_page.locator("a[data-nclk='TAA.price']")
                    if "is-ascending" not in price_btn.get_attribute("class") or "":
                        price_btn.click(timeout=3000)
                        target_page.wait_for_selector("a[data-nclk='TAA.price'].is-ascending", timeout=4000)
                        time.sleep(1)
                    
                    cards = target_page.locator(".item_inner").all()[:10]
                    found_price = None
                    display_price = None
                    article_url = None
                    
                    for card in cards:
                        c_text = card.inner_text()
                        if "지분" in c_text or "보류지" in c_text or "경매" in c_text:
                            continue
                            
                        price_text = card.locator(".price").first.inner_text().strip()
                        price_num = parse_korean_price(price_text)
                        
                        if price_num > 100000000:
                            found_price = price_num
                            display_price = price_text
                            break
                            
                    if found_price:
                        print(f"   [{ptp_nm:<7} / 전용 {ex_area:>5}] -> 최저가: {display_price} ({found_price:,}원)")
                        all_results.append({
                            "crawled_date": today_str,
                            "complex_no": complex_no_db,
                            "naver_complex_no": nid,
                            "complex_name": apt_name,
                            "ptp_name": ptp_nm,
                            "ptp_no": ptp_no,
                            "exclusive_area": ex_area,
                            "supply_area": sup_area,
                            "lowest_ask": found_price,
                            "article_url": article_url
                        })
                        return True
                    else:
                        print(f"   [{ptp_nm:<7} / 전용 {ex_area:>5}] -> 정상매물 없음 (메타데이터 보존)")
                        all_results.append({
                            "crawled_date": today_str,
                            "complex_no": complex_no_db,
                            "naver_complex_no": nid,
                            "complex_name": apt_name,
                            "ptp_name": ptp_nm,
                            "ptp_no": ptp_no,
                            "exclusive_area": ex_area,
                            "supply_area": sup_area,
                            "lowest_ask": 0,
                            "article_url": None
                        })
                        return True
                        
                except Exception as e:
                    print(f"   [{ptp_nm:<7} / 전용 {ex_area:>5}] ⚠️ 수집 에러 발생 (재시도 큐 대기): {e}")
                    return False
                finally:
                    target_page.close()
            
            for p_type in combined_ptps:
                success = process_ptp(p_type, 0)
                if not success:
                    failed_queue.append(p_type)
            
            # Retry logic
            retries = 0
            while failed_queue and retries < 2:
                retries += 1
                import time
                print(f"   🔄 실패한 {len(failed_queue)}개 평형 재시도 {retries}/2 ... (3초 대기)")
                time.sleep(3)
                current_failed = failed_queue.copy()
                failed_queue.clear()
                
                for p_type in current_failed:
                    success = process_ptp(p_type, retries)
                    if not success:
                        failed_queue.append(p_type)

                    
        try:
            if 'context' in locals(): context.close()
            if 'browser' in locals(): browser.close()
        except: pass
        
    print(f"\n✅ 진짜 시세 검증 완료! 총 {len(all_results)}건 수집됨.")
    
    out_path = os.path.join(os.path.dirname(__file__), output_filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"📦 로컬에 데이터 백업(자산화) 완료: {output_filename}")

if __name__ == "__main__":
    run_master()
