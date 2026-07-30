import os, sys, requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
import json

cid_1_5 = '94379391-ef97-4ce2-a4a1-bcb00a070ba7'
cid_shin = 'dd976eb4-fbfd-4fce-acae-e043a72c21c9'

aliases = {
    cid_1_5: ["현대1,2차", "현대3차", "현대4차", "현대5차", "현대1차", "현대3", "현대4", "현대5", "구현대", "현대(1", "현대(3", "현대(4"],
    cid_shin: ["현대", "현대9차", "현대11차", "현대12차", "신현대", "현대아파트"]
}

def clean_name(n):
    import re
    return re.sub(r'\(.*?\)', '', n).replace(' ', '').strip()

def get_cid(api_name):
    ci = clean_name(api_name)
    for cid, alist in aliases.items():
        if ci == clean_name(cid): return cid
        for al in alist:
            if ci == clean_name(al):
                return cid
    return None

import urllib.request
import urllib.parse
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
molit_key = unquote(os.environ.get('RTMS_API_KEY'))
req_url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
params = {'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': '202405'}
r = requests.get(req_url, params=params)
root = ET.fromstring(r.content)
for item in root.findall('.//item'):
    umdNm = item.findtext('umdNm')
    if not umdNm or '압구정' not in umdNm: continue
    aptNm = item.findtext('aptNm')
    if '11차' in aptNm:
        print(f"APT: {aptNm.encode('utf-8')}, Cleaned: {clean_name(aptNm).encode('utf-8')}, CID: {get_cid(aptNm)}")
