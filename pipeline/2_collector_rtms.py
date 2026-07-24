import os
import sys
import io
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client
import urllib.parse

# 윈도우 인코딩 에러 방지용 (이모지 출력)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 환경변수 로딩
load_dotenv()
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
RTMS_API_KEY = os.environ.get("RTMS_API_KEY")

if not RTMS_API_KEY:
    print("❗ 에러: .env 파일에 RTMS_API_KEY 가 없습니다.")
    sys.exit(1)

supabase: Client = create_client(URL, KEY)

def fetch_rtms_data(lawd_cd, deal_ymd):
    # 국토부 아파트매매 실거래 상세 자료 API 엔드포인트 (신규 게이트웨이)
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    
    # 공공데이터 API 키는 이중 인코딩을 피하기 위해 unquote 처리하는 편이 안전합니다.
    safe_key = urllib.parse.unquote(RTMS_API_KEY)
    
    params = {
        "serviceKey": safe_key,
        "LAWD_CD": lawd_cd,
        "DEAL_YMD": deal_ymd,
        "numOfRows": "1000",
        "pageNo": "1"
    }
    
    try:
        res = requests.get(url, params=params, timeout=15)
        res.raise_for_status()
        return res.content
    except Exception as e:
        print(f"API 요청 에러: {e}")
        return None

def run_rtms_crawler():
    print("🚀 국토교통부 실거래가 수집 시작...")
    
    # 1. DB에서 우리가 수집하는 아파트 단지 목록 가져오기
    complexes_data = supabase.table("complexes").select("*").execute().data
    if not complexes_data:
        print("DB에 저장된 아파트 단지가 없습니다.")
        return

    # 국토부 API는 구/군 지역별(5자리) 묶어서 요청해야 함. 
    # ex) 송파구 가락동(1171010700) -> 송파구(11710) 추출
    lawd_codes = {c['bjd_code'][:5] for c in complexes_data if c.get('bjd_code')}
    
    # 테스트용: '지난달'을 기준으로 데이터 가져오기 (보통 실거래가 등록 기한은 한 달이므로 가장 꽉 찬 데이터)
    last_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime("%Y%m")
    
    for lawd_cd in lawd_codes:
        print(f"\n📡 지역코드 [{lawd_cd}] 실거래가 파싱 중... (대상 월: {last_month})")
        xml_data = fetch_rtms_data(lawd_cd, last_month)
        
        if not xml_data:
            continue
            
        try:
            # 반환된 XML 데이터 파싱 (바이트 그대로 전달하여 XML 내부 인코딩 선언을 따름)
            root = ET.fromstring(xml_data)
            
            items = root.findall(".//item")
            if not items:
                result_msg = root.find(".//resultMsg")
                msg = result_msg.text if result_msg is not None else "결과 없음(또는 에러)"
                print(f"⚠️ 공공API 데이터 없음 또는 오류: {msg}")
                continue
                
            print(f"✅ 수신 성공! 해당 지역에 총 {len(items)}건의 일반 거래가 있었습니다.")
            
            # 수신된 거래 내역들 중에 우리가 모니터링 중인 KB 50 아파트가 있는지 필터링 테스트
            found_deals = False
            for item in items:
                apt_name_node = item.find('아파트')
                if apt_name_node is None:
                    continue
                    
                apt_name = apt_name_node.text.strip()
                price = item.find('거래금액').text.strip().replace(',', '')
                day = item.find('일').text.strip()
                
                # DB의 타겟 아파트들과 이름 매칭
                for c in complexes_data:
                    # 이름 텍스트 포함 여부로 간단히 식별 (정교한 로직은 추후 추가)
                    if c['name'] in apt_name or apt_name in c['name']:
                        print(f"   🎉 매칭 완료! [{apt_name}] 실거래 발견 👉 {last_month}월 {day}일 계약, 가격: {price}만원")
                        found_deals = True
            
            if not found_deals:
                print("   🤔 이번 달 해당 지역 수신 내역 중 모니터링 대상(대장주) 아파트 거래는 없네요.")
                        
        except Exception as e:
            print(f"XML 파싱 에러: {e}")

if __name__ == "__main__":
    run_rtms_crawler()
