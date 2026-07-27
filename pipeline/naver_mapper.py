import os
import json
import re
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from supabase import create_client

load_dotenv("d:/appmaking/kb50_mdd/pipeline/.env")
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])

def build_mapping():
    data = supabase.table("complexes").select("*").execute().data
    mapping = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) # 디버깅용 UI 켜기
        context = browser.new_context(user_agent="Mozilla/5.0")
        page = context.new_page()
        
        for idx, c in enumerate(data):
            name = c["name"]
            
            try:
                page.goto("https://new.land.naver.com/complexes/", wait_until="domcontentloaded")
                time.sleep(1)
                
                # 네이버 부동산 검색창 (클래스명 등은 상황에 맞게)
                search_input = page.locator(".search_input")
                search_input.fill(name)
                page.keyboard.press("Enter")
                
                # 검색 후 URL이 complexes/12345 로 바뀌는지 대기
                try:
                    page.wait_for_url(re.compile(r"complexes/\d+"), timeout=4000)
                except:
                    # 클릭형 자동완성이 나오면 첫번째 것 클릭
                    try:
                        page.locator(".auto_complete_wrap .search_list li").first.click(timeout=3000)
                        page.wait_for_url(re.compile(r"complexes/\d+"), timeout=4000)
                    except:
                        pass

                current_url = page.url
                match = re.search(r"complexes/(\d+)", current_url)
                if match:
                    naver_id = match.group(1)
                    mapping[str(c["complex_no"])] = naver_id
                    print(f"[{idx+1}/{len(data)}] {name} -> {naver_id}")
                else:
                    print(f"[{idx+1}/{len(data)}] {name} -> ❌ 실패")
                    
            except Exception as e:
                print(f"Failed {name}: {e}")
                
        browser.close()
        
    with open("d:/appmaking/kb50_mdd/pipeline/naver_complex_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    print("매핑 완료!")

if __name__ == "__main__":
    build_mapping()
