import os
import sys
import io
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()
RTMS_API_KEY = os.environ.get("RTMS_API_KEY")

LAWD_CD = "11710" # 송파구
APT_NAME = "헬리오시티"
TARGET_AREA = 84.0 # 전용면적 기준 (84.xx)

def fetch_month(deal_ymd):
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = urllib.parse.unquote(RTMS_API_KEY)
    params = {
        "serviceKey": safe_key,
        "LAWD_CD": LAWD_CD,
        "DEAL_YMD": deal_ymd,
        "numOfRows": "1000",
        "pageNo": "1"
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
        return deal_ymd, res.content
    except Exception as e:
        return deal_ymd, None

def run_heliocity_10y_poc():
    print(f"🚀 [MVP 테스트] '{APT_NAME}' (전용 {TARGET_AREA}㎡대) 10년치 국토부 데이터 추출 기동...")
    
    # 2016년 8월부터 2026년 7월(현재)까지 120개월 생성 (현 시점 기준 10년)
    now = datetime(2026, 7, 1) # User 님이 계신 현재 시점 기준
    months_to_fetch = []
    for i in range(120):
        m = now - relativedelta(months=i)
        months_to_fetch.append(m.strftime("%Y%m"))
    
    heliocity_deals = []
    
    print(f"⏳ 총 {len(months_to_fetch)}개월 순회 조회를 시작합니다 (멀티쓰레딩 5개 병렬 진행)...")
    
    # 공공데이터 API 부하 방지를 위해 max_workers=3 정도로 제한
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_month, ym): ym for ym in months_to_fetch}
        
        count = 0
        for future in as_completed(futures):
            ym, xml_data = future.result()
            count += 1
            
            if count % 10 == 0:
                print(f"   ... {count}/{len(months_to_fetch)} 개월 완료")
                
            if not xml_data:
                continue
                
            try:
                root = ET.fromstring(xml_data)
                items = root.findall(".//item")
                for item in items:
                    apt_node = item.find('아파트')
                    area_node = item.find('전용면적')
                    
                    if apt_node is None or area_node is None:
                        continue
                        
                    n = apt_node.text.strip()
                    area = float(area_node.text.strip())
                    
                    # '헬리오시티' 이고, 전용면적이 84점대 (84.xx) 인 것만 필터링
                    if APT_NAME in n and 84.0 <= area < 86.0: # 84~85 평형대 포용
                        price_str = item.find('거래금액').text.strip().replace(',', '')
                        day = item.find('일').text.strip().zfill(2)
                        
                        heliocity_deals.append({
                            'date': f"{ym[:4]}-{ym[4:]}-{day}",
                            'price': int(price_str) * 10000, # 만원 단위를 원 단위로 변환
                            'area': area
                        })
            except Exception as e:
                pass

    print(f"\n✅ 데이터 수집 완료! 총 {len(heliocity_deals)}건의 헬리오시티 84㎡ 실거래가 파악됨.")
    
    if not heliocity_deals:
        print("데이터를 찾을 수 없습니다. API 키나 호출 방식을 확인하세요.")
        return
        
    import json
    
    # 가격 순 정렬 및 역대 최고가 도출
    heliocity_deals.sort(key=lambda x: x['price'], reverse=True)
    ath = heliocity_deals[0]
    print(f"\n🏆 [역대 최고가 (ATH)]")
    print(f"   - 시기: {ath['date']}")
    print(f"   - 거래액: {ath['price']:,}원")
    
    # 시간 순 정렬 후 최근 1~2달 내역 도출 (최신 데이터 확보를 위해)
    heliocity_deals.sort(key=lambda x: x['date'], reverse=True)
    
    recent_deals = heliocity_deals[:10] # 가장 최근 10건
    
    print(f"\n🔥 [최근 실거래 현황 (상위 10건)]")
    if recent_deals:
        prices = [d['price'] for d in recent_deals]
        print(f"   - 최저 거래가: {min(prices):,}원")
        print(f"   - 최고 거래가: {max(prices):,}원")
        for d in recent_deals[:5]:
            print(f"       > {d['date']} | {d['price']:,}원")
            
    # 프론트엔드에서 읽을 수 있게 API 대용 JSON 파일 생성
    output_path = os.path.join(os.path.dirname(__file__), "../web/public/heliocity_10y.json")
    with open(output_path, "w", encoding='utf-8') as f:
        json.dump({
            "ath": ath,
            "recent_deals": recent_deals,
            "total_deals": len(heliocity_deals),
            "history": heliocity_deals
        }, f, ensure_ascii=False, indent=2)
    print(f"\n💾 web/public/heliocity_10y.json 저장 완료! 프론트엔드에서 즉시 사용 가능합니다.")

if __name__ == "__main__":
    run_heliocity_10y_poc()
