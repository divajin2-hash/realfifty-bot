import re

with open('pipeline/10_full_pyeong_scraper.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_logic = """
            failed_queue = []
            
            def process_ptp(p_type, retry_count=0):
                ptp_no = p_type.get('pyeongNo') or p_type.get('ptpNo')
                ptp_nm = p_type.get('pyeongName') or p_type.get('pyeongNm')
                ex_area = float(p_type.get('exclusiveArea', 0))
                nid = p_type.get('_naver_id')
                
                target_url = f"https://new.land.naver.com/complexes/{nid}?a=APT&b=A1&ptpNo={ptp_no}"
                
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
                            "lowest_ask": found_price,
                            "article_url": article_url
                        })
                        return True
                    else:
                        print(f"   [{ptp_nm:<7} / 전용 {ex_area:>5}] -> 정상매물 없음")
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
"""

pattern = re.compile(r'\s+for p_type in combined_ptps:.*?finally:\n\s+target_page\.close\(\)', re.DOTALL)
if pattern.search(text):
    new_code = pattern.sub(new_logic, text)
    with open('pipeline/10_full_pyeong_scraper.py', 'w', encoding='utf-8') as f:
        f.write(new_code)
    print("Scraper successfully refactored.")
else:
    print("Could not find the target block to replace.")
