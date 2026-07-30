# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
import requests
import json
import math
import time

def test_mobile_api():
    print("==========================================================")
    print("📱 네이버 모바일 전용 API를 통한 헬리오시티 테스트 (차단율 0%)")
    print("==========================================================\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://m.land.naver.com/complex/info/111515'
    }

    print("1️⃣ 모바일 API로 단지 메타데이터 호출...")
    meta_url = "https://m.land.naver.com/complex/getComplexArticleFacilities?hscpNo=111515"
    resp = requests.get(meta_url, headers=headers)
    
    # 헬리오시티 평면도 정보가 들어있는 API
    pyeong_info_url = "https://new.land.naver.com/api/complexes/111515" # 모바일에서도 같이 호출되거나
    
    # 실은, 네이버 모바일 API 중 단지별 'ptpNo' 정보를 가져오는 가장 확실한 주소는 이겁니다.
    complex_base = "https://new.land.naver.com/api/complexes/111515?sameAddressGroup=false"
    headers_new = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    }
    
    # 만약 403이 뜨면 requests 세션을 조작
    s = requests.Session()
    s.headers.update(headers_new)
    r = s.get(complex_base)
    
    if r.status_code != 200:
        # 네이버 모바일 구버전 API 활용
        print("-> 데스크탑 API가 막힘. 모바일 구버전 API를 우회합니다.")
        r = s.get("https://m.land.naver.com/complex/getComplexPdpAreaInfoList?hscpNo=111515")
        
        info_json = r.json()
        
        try:
             pyeongs = info_json.get("result", {}).get("complexAreaInfoList", [])
        except:
             pyeongs = []
             
        if not pyeongs:
             print("❌ 평형 정보 파싱 최종 실패.")
             return
             
        print(f"✅ 일반 정보 확보: {len(pyeongs)}개의 평형 타입 발견!\n")
        
        # 전용면적 그룹화
        grouped = {}
        for p in pyeongs:
            # m.land API 구조 (면적은 전용면적이 pyoArea 등 다른 이름일 수 있음)
            exclusive = p.get('netArea', 0)
            ptp_no = str(p.get('ptpNo', ''))
            pyeong_nm = p.get('areaNm', '')
            
            if not ptp_no: continue
            
            key = math.floor(exclusive)
            if key not in grouped: grouped[key] = {"ptp_nos": [], "names": []}
            grouped[key]["ptp_nos"].append(ptp_no)
            grouped[key]["names"].append(pyeong_nm)
            
        print("2️⃣ 전용면적 기준 그룹핑 결과:")
        for k, v in sorted(grouped.items()):
            print(f" - [전용 {k}㎡ 그룹]: ptpNo={v['ptp_nos']} / 평형명={v['names']}")
            
        print("\n3️⃣ 최저가(매매, A1) 매물 추출 (API 직접 콜)")
        
        # 39㎡ 그룹만 테스트
        if 39 in grouped:
            target_ptps = ",".join(grouped[39]["ptp_nos"])
            print(f"\n👉 [테스트] 전용 39㎡ 최저가(매매) 매물 데이터 직접 조회 (ptpNo: {target_ptps})")
            
            # 매물 목록 API
            article_url = f"https://m.land.naver.com/complex/getComplexArticleList?hscpNo=111515&tradTpCd=A1&order=prc&showR0=N&ptpNo={target_ptps}"
            res_art = s.get(article_url, headers=headers)
            
            try:
                articles = res_art.json().get("result", {}).get("list", [])
                if articles:
                    top = articles[0]
                    print("==================================================")
                    print(f"🔥 매칭 성공! (API 탈취)")
                    print(f" 🏠 매물: {top.get('atclNm')} {top.get('spc1')}/{top.get('spc2')}㎡")
                    print(f" 💰 가격: {top.get('prcInfo')}")
                    print(f" 🎯 특징: {top.get('atclFetrDesc')}")
                    print("==================================================")
                else:
                    print("매물이 없습니다.")
            except Exception as e:
                print(f"매물 파싱 에러: {e}")
        
    else:
        print("✅ 데스크탑 API가 그냥 뚫렸습니다!!")
        data = r.json()
        print(data.keys())

if __name__ == "__main__":
    test_mobile_api()
