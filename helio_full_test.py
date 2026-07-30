# -*- coding: utf-8 -*-
import sys
import io
import time
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

def run_heliocity_full_test():
    with sync_playwright() as p:
        print("==========================================================")
        print("🏢 헬리오시티(111515) 전 평형 실시간 최저가 검증 테스트")
        print("==========================================================\n")
        
        # 봇 탐지 회피
        browser = p.chromium.launch(headless=False, args=['--disable-blink-features=AutomationControlled'])
        ctx = browser.new_context(user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36')
        ctx.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = ctx.new_page()

        # 1. 네이버 평형 메타데이터 API 직접 호출 (안전성 검증됨)
        print("1️⃣ 헬리오시티 단지 평면도 API 호출 중...")
        r = page.goto('https://new.land.naver.com/api/complexes/111515', wait_until='domcontentloaded')
        time.sleep(1)
        data = r.json()
        pyeongs = data.get('complexPyeongDetailList', [])
        
        if not pyeongs:
            print("❌ 평형 정보를 불러오지 못했습니다.")
            browser.close()
            return
            
        print(f"✅ 총 {len(pyeongs)}개의 네이버 고유 타입(ptpNo)이 발견되었습니다.\n")

        # 2. 전용면적 기준으로 타입(ptpNo) 묶기
        # 국토부 매방식을 고려하여 전용면적의 정수 부분(예: 39.12 -> 39, 84.99 -> 84)을 키값으로 묶습니다.
        grouped_pyeongs = {}
        for py in pyeongs:
            exclusive = py.get('exclusiveArea', 0)
            ptp_no = str(py.get('ptpNo'))
            pyeong_nm = py.get('pyeongNm')
            
            # 정수 단위로 그룹화 (국토부 매칭 기준)
            area_key = int(exclusive) 
            
            if area_key not in grouped_pyeongs:
                grouped_pyeongs[area_key] = {"ptp_nos": [], "names": []}
                
            grouped_pyeongs[area_key]["ptp_nos"].append(ptp_no)
            grouped_pyeongs[area_key]["names"].append(pyeong_nm)

        print(f"2️⃣ 전용면적 기준으로 총 {len(grouped_pyeongs)}개의 그룹으로 완벽히 압축되었습니다.")
        print("-" * 50)
        
        # 3. 그룹별 최저가 조회 루프
        print("3️⃣ 각 평형 그룹별 실시간 최저호가(매매)를 산출합니다.\n")
        
        for area_key, info in sorted(grouped_pyeongs.items()):
            ptp_nos_str = ",".join(info["ptp_nos"])
            names_str = ", ".join(info["names"])
            
            print(f"■ 전용 {area_key}㎡ 그룹 (네이버 묶음: {names_str})")
            
            # API 호출 (매매 A1, 낮은가격순 prcSort=asc) - 필터링 URL로 이동하여 결과 UI 렌더링 대기
            url = f"https://new.land.naver.com/complexes/111515?a=APT&b=A1&ptpNo={ptp_nos_str}&prcSort=asc"
            page.goto(url, wait_until='domcontentloaded')
            
            try:
                # 리스트 아이템이 뜰 때까지 대기
                page.wait_for_selector('.item_inner', timeout=5000)
                time.sleep(1) # 내부 JS 렌더링 안정화 대기
                
                card = page.locator('.item_inner').first
                price = card.locator('.price').first.inner_text().strip()
                spec = card.locator('.spec').first.inner_text().strip()
                
                # 경매, 지분 등 가짜 매물 필터링 (간단 버전)
                text_content = card.inner_text()
                if "지분" in text_content or "경매" in text_content:
                    print(f"   => ⚠️ 주의: 1순위 매물에 특수조건(지분/경매) 포함됨.")
                
                print(f"   => 🏆 최저가: {price} | 노출스펙: {spec.split(',')[0]}")
            except Exception as e:
                print(f"   => ❌ 매물 없음 (또는 읽기 실패)")
                
            print("-" * 50)

        browser.close()
        print("✅ 헬리오시티 전 평형 검증 완료!")

if __name__ == "__main__":
    run_heliocity_full_test()
