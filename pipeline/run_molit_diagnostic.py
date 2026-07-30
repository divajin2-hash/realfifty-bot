import os, requests
from xml.etree import ElementTree as ET
from urllib.parse import unquote

key = unquote(os.environ.get("RTMS_API_KEY"))
url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
names = set()
for m in ['202305', '202306', '202307', '202401', '202402']:
    params = {'serviceKey': key, 'LAWD_CD': '11680', 'DEAL_YMD': m}
    r = requests.get(url, params=params)
    try:
        root = ET.fromstring(r.text)
        for item in root.findall('.//item'):
            if '현대' in item.findtext('aptNm'):
                names.add(item.findtext('aptNm'))
    except: pass
print("Found MOLIT names:", list(names))
