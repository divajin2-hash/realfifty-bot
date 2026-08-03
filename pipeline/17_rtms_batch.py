import os
import sys
import io
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from supabase import create_client, Client
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

load_dotenv('pipeline/.env')
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
RTMS_KEY = os.environ.get("RTMS_API_KEY")

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

def run_rtms_10y_batch():
    print("=========================================================")
    print("🔥 [17번 배치] 전국 50대장 10년 치 실거래가 광역 싹쓸이 가동 🔥")
    print("=========================================================")
    
    complexes = supabase.table("complexes").select("*").execute().data
    if not complexes:
        print("DB에 아파트 정보가 없습니다.")
        return
        
    lawd_map = {}
    for c in complexes:
        lcd = c["bjd_code"][:5]
        if lcd not in lawd_map: lawd_map[lcd] = []
        lawd_map[lcd].append(c)
        
    print(f"👉 총 {len(lawd_map)}개의 법정구(지역) 단위로 클러스터링을 완료했습니다.")
    
    url = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
    safe_key = unquote(RTMS_KEY)
    
    # 2014년 ~ 2024년 (10년 이상 전체 핫사이클 탐색)
    years = range(2014, 2025)
    months = range(1, 13)
    
    total_inserted = 0
    
    for y in years:
        for m in months:
            ymd = f"{y}{m:02d}"
            if y == 2024 and m > 7: continue # 미래 건너뛰기
            
            print(f"\n▶ 📅 조회 연월: {ymd}")
            trades_to_insert = []
            
            for lawd_cd, apts in lawd_map.items():
                params = {
                    "serviceKey": safe_key,
                    "LAWD_CD": lawd_cd,
                    "DEAL_YMD": ymd,
                    "numOfRows": "2000",
                    "pageNo": "1"
                }
                
                try:
                    res = requests.get(url, params=params, timeout=10)
                    if res.status_code != 200: continue
                    root = ET.fromstring(res.content)
                    
                    for item in root.findall(".//item"):
                        item_apt = item.findtext("aptNm")
                        if not item_apt: continue
                        
                        # 50개 단지 목록과 매칭되는지 확인 (문자열 포함 여부)
                        matched_c = None
                        for c in apts:
                            # 괄호 등 특수문자가 있어서 이름 매칭 시 주의해야 함
                            db_name = c["name"].replace("(", "").replace(")", "").replace(" ", "")
                            api_name = item_apt.replace("(", "").replace(")", "").replace(" ", "")
                            if db_name in api_name or api_name in db_name:
                                matched_c = c
                                break
                                
                        if not matched_c: continue
                        
                        price = format_price(item.findtext("dealAmount"))
                        area_exact = float(item.findtext("excluUseAr"))
                        mk = int(round(area_exact))
                        if matched_c["id"] == '94379391-ef97-4ce2-a4a1-bcb00a070ba7' and abs(area_exact - 82.23) < 0.01:
                            mk = 83
                        day = item.findtext("dealDay")
                        d_str = f"{y}-{m:02d}-{int(day):02d}"
                        floor = int(item.findtext("floor", "0"))
                        deal_type = item.findtext("dealingGbn", " ") # '직거래' or '중개거래' or empty
                        
                        trades_to_insert.append({
                            "complex_id": matched_c["id"],
                            "match_key_area": mk,
                            "deal_date": d_str,
                            "deal_price": price,
                            "floor": floor,
                            "exclusive_area_exact": area_exact,
                            "transaction_type": deal_type
                        })
                except Exception as e:
                    pass
                
                # 공공데이터 API Rate Limit 방지
                time.sleep(0.05)
                
            # 매 달 단위로 모인 데이터를 Supabase로 전송 (속도 최적화)
            if trades_to_insert:
                try:
                    supabase.table("rtms_transactions").upsert(
                        trades_to_insert, 
                        on_conflict="complex_id, match_key_area, deal_date, deal_price, floor"
                    ).execute()
                    total_inserted += len(trades_to_insert)
                    print(f"   ✅ {ymd} -> {len(trades_to_insert)}건의 50대장 거래 로그 적재 완료 (누적: {total_inserted}건)")
                except Exception as e:
                    print(f"      [!] DB 적재 지연: {e}")
                    pass

    print(f"\n🎉 10년 치 역사적 실거래가 원본 테이블에 총 {total_inserted}건 적재 완료!")

if __name__ == "__main__":
    run_rtms_10y_batch()
