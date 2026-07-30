import requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
import sys; sys.stdout.reconfigure(encoding='utf-8')
import os
from dotenv import load_dotenv
load_dotenv('d:/appmaking/kb50_mdd/pipeline/.env')
key = unquote(os.environ['RTMS_API_KEY'])

url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'

# 여러 월을 검색해서 반포동에서 "한신" 이름 찾기
for ym in ['202501', '202506', '202601', '202506', '202406', '202301', '202206', '202101']:
    r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11650', 'DEAL_YMD': ym, 'numOfRows': 3000}, timeout=8)
    root = ET.fromstring(r.content)
    for item in root.findall('.//item'):
        apt = item.findtext('aptNm', '')
        umd = item.findtext('umdNm', '')
        if '반포' in umd and ('한신' in apt or '신반포' in apt):
            ar = float(item.findtext('excluUseAr', '0'))
            pr = int(item.findtext('dealAmount', '0').replace(',','').strip()) * 10000
            print(f"[{ym}] {apt} | {umd} | {ar}㎡ | {pr:,}원")

# 잠원동도 확인 (신반포한신2차가 잠원동일 수 있음)
print("\n--- 잠원동 검색 ---")
for ym in ['202501', '202506', '202601', '202406', '202301']:
    r = requests.get(url, params={'serviceKey': key, 'LAWD_CD': '11650', 'DEAL_YMD': ym, 'numOfRows': 3000}, timeout=8)
    root = ET.fromstring(r.content)
    for item in root.findall('.//item'):
        apt = item.findtext('aptNm', '')
        umd = item.findtext('umdNm', '')
        if '잠원' in umd and ('한신' in apt or '신반포' in apt):
            ar = float(item.findtext('excluUseAr', '0'))
            pr = int(item.findtext('dealAmount', '0').replace(',','').strip()) * 10000
            print(f"[{ym}] {apt} | {umd} | {ar}㎡ | {pr:,}원")
