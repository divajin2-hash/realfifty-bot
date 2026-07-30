import os, requests, json
from xml.etree import ElementTree as ET
from urllib.parse import unquote
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
molit_key = unquote(os.environ.get('RTMS_API_KEY'))
req_url = 'http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev'
names = []
for m in ['202305', '202306', '202307', '202401', '202402', '202407']:
    params = {'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': m}
    r = requests.get(req_url, params=params)
    try:
        root = ET.fromstring(r.text)
        for item in root.findall('.//item'):
            if item.findtext('umdNm') and '압구정' in item.findtext('umdNm'):
                if '현대' in item.findtext('aptNm'):
                    names.append(f"{item.findtext('aptNm')} {item.findtext('excluUseAr')}")
    except: pass
with open('debug_names.json', 'w', encoding='utf-8') as f:
    json.dump(names, f, ensure_ascii=False, indent=2)
