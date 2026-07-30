# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import time
import re
import math
from playwright.sync_api import sync_playwright

def run_heliocity_html_regex():
    with sync_playwright() as p:
        print("==========================================================")
        print("🏢 헬리오시티(111515) 전 평형 매핑 및 최저가 증명 (HTML 정규식판)")
        print("==========================================================\n")
        
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36')
        page = ctx.new_page()

        # 1. 헬리오시티 접속
        url = 'https://new.land.naver.com/complexes/111515?ms=37.497554,127.10649,17&a=APT&b=A1&e=RETAIL'
        print("1️⃣ 사람처럼 헬리오시티 페이지 접속 중...")
        page.goto(url, wait_until='domcontentloaded', timeout=12000)
        time.sleep(3) # 페이지가 그려질 때까지 대기
        
        html_content = page.content()
        
        # 2. HTML 소스에서 평형 메타데이터(JSON 포맷 텍스트)를 정규식으로 직접 발췌
        print("2️⃣ HTML 원본에서 평형 데이터(ptpNo, 전용면적) 강제 추출 중...")
        
        # 네이버 소스 내에는 "complexPyeongDetailList":[{"ptpNo":"1","ptpNm":"61A",...}] 형태의 데이터가 문자열로 박혀있음
        match = re.search(r'"complexPyeongDetailList"\s*:\s*(\[.*?\])', html_content)
        
        if not match:
            # 다른 변수명으로 저장되었을 수도 있으니 강제로 exclusiveArea 와 ptpNo 쌍을 모두 찾음
            # 예: "ptpNo":"1","ptpNm":"61C","supplyAreaDouble":61.02,"exclusiveArea":39.12
            print(" -> 패턴 A 실패. 패턴 B(Raw Regex) 탐색...")
            ptp_blocks = re.findall(r'{"ptpNo":"?(\d+)"?,"ptpNm":"?([^"]+)"?[^}]*"exclusiveArea":([0-9.]+)', html_content)
        else:
            import json
            try:
                pyeong_list = json.loads(match.group(1))
                ptp_blocks = [(str(p.get("ptpNo")), p.get("pyeongNm"), p.get("exclusiveArea")) for p in pyeong_list]
            except:
                ptp_blocks = []
                
        if not ptp_blocks:
            # 마지막 수단: 깡 정규식
            ptp_blocks = re.findall(r'"ptpNo":"?(\d+)"?[^}]+"exclusiveArea":([0-9.]+)', html_content)
            # pyeongNm 이 멀리 있을 수 있으므로 단순화
            ptp_blocks = [(p[0], f"타입{p[0]}", float(p[1])) for p in ptp_blocks]
            
        if not ptp_blocks:
            print("❌ HTML 원문 내에서도 평형 정보를 찾지 못했습니다. (네이버 UI 구조 전면 개편 추정)")
            browser.close()
            return

        print(f"✅ 추출 성공! (평형 데이터 {len(ptp_blocks)}개 확보)\n")
        
        # 3. 전용 면적 버림(floor) 결과로 그룹핑
        grouped = {}
        for ptp_no, ptp_nm, exc_area in ptp_blocks:
            area_key = math.floor(float(exc_area))
            
            if area_key not in grouped:
                grouped[area_key] = {"ptp_nos": [], "names": []}
            
            if ptp_no not in grouped[area_key]["ptp_nos"]: # 중복 제거
                grouped[area_key]["ptp_nos"].append(ptp_no)
                grouped[area_key]["names"].append(ptp_nm)
                
        print(f"3️⃣ 국토부 매칭용 '전용면적' 기준 그룹화 (총 {len(grouped)}개)\n")
        
        # 4. 헬리오시티 39㎡ 그룹만 집중 타겟팅하여 최저가 확인
        target_area = 39
        if target_area in grouped:
            info = grouped[target_area]
            ptps = ",".join(info["ptp_nos"])
            nms = ", ".join(info["names"])
            
            print(f"🔎 타겟 그룹: 전용 {target_area}㎡ (네이버 표기: {nms})")
            print(f"👉 결합된 ptpNo 파라미터: {ptps}")
            
            # 5. 기존 18번 파이프라인의 안전한 브라우저 이동 방식 사용
            target_url = f"https://new.land.naver.com/complexes/111515?a=APT&b=A1&ptpNo={ptps}&prcSort=asc"
            print(f"\n👉 낮은가격순 정렬 페이지로 이동: {target_url}\n")
            
            page.goto(target_url, wait_until='domcontentloaded', timeout=12000)
            
            try:
                page.wait_for_selector('.item_inner', timeout=8000)
                time.sleep(1.5)
                
                # 리스트 매물 중 특수매물(경매, 지분 등)이 아닌 첫 번째 '정상 최저가' 찾기
                cards = page.locator('.item_inner').all()[:5]
                for card in cards:
                    text_content = card.inner_text().strip()
                    if "지분" in text_content or "경매" in text_content or "보류지" in text_content:
                        continue
                        
                    price = card.locator('.price').first.inner_text().strip()
                    spec = card.locator('.spec').first.inner_text().strip()
                    
                    print("==================================================")
                    print(f"🔥 네이버 '전용 39㎡' (61A, 61D 등 병합) 실시간 최저호가 추출 완벽 성공! 🔥")
                    print(f" 🏠 노출 평형: {spec.split(',')[0]}")
                    print(f" 💰 실 최저가: {price}")
                    print("==================================================")
                    break
                    
            except Exception as e:
                print(f"❌ 매물 리스트 파싱 실패: {e}")
        else:
            print(f"⚠️ 전용면적 {target_area}㎡ 그룹을 찾을 수 없습니다. (현재 헬리오시티에 면적이 다르게 저장되어 있을 수 있음)")
            
        browser.close()

if __name__ == "__main__":
    run_heliocity_html_regex()
