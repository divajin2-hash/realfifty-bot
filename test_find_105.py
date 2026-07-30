import os, requests, json
from xml.etree import ElementTree as ET
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
molit_key = unquote(os.environ.get('RTMS_API_KEY'))
req_url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
for y in ['202305', '202306', '202404', '202405', '202406']:
    params = {'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': y}
    r = requests.get(req_url, params=params)
    root = ET.fromstring(r.text)
    for item in root.findall('.//item'):
        if item.findtext('umdNm') and '압구정' in item.findtext('umdNm'):
            if '105' in item.findtext('dealAmount') or '183' in item.findtext('excluUseAr'):
                print(f"[{y}] Found: {item.findtext('aptNm')} {item.findtext('dealAmount')} {item.findtext('excluUseAr')}")
