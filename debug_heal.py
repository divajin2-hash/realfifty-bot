import os, sys, requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
molit_key = unquote(os.environ.get('RTMS_API_KEY'))

cid_1_5 = '94379391-ef97-4ce2-a4a1-bcb00a070ba7'
aliases = ["현대1,2차", "현대3차", "현대4차", "현대5차", "현대1차", "현대3", "현대4", "현대5", "구현대", "현대(1", "현대(3", "현대(4", "현대1", "현대2", "현대2차"]
import re
def clean_name(n):
    return re.sub(r'\(.*?\)', '', n).replace(" ", "").strip()

for ym in ['202601', '202605']:
    r = requests.get('http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev', params={'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': ym, 'numOfRows': 1000})
    root = ET.fromstring(r.text)
    for item in root.findall('.//item'):
        aptNm = item.findtext('aptNm')
        umdNm = item.findtext('umdNm')
        if "현대" in aptNm and "압구정" in umdNm:
            c_name = clean_name(aptNm)
            print(f"[{ym}] Found: {aptNm} -> cleaned: {c_name}")
            if c_name in aliases:
                print("  => Mapped to 1~5th!")
