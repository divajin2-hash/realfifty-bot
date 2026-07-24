import os
import urllib.request as request
import xml.etree.ElementTree as ET
from dotenv import load_dotenv

load_dotenv('pipeline/.env')
url = f"http://openapi.molit.go.kr:8081/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTrade?LAWD_CD=11680&DEAL_YMD=202110&serviceKey={os.environ.get('RTMS_API_KEY')}"

try:
    res = request.urlopen(url)
    xml_data = res.read().decode('utf-8')
    print("XML Response snippet:")
    print(xml_data[:1000])
    
    root = ET.fromstring(xml_data)
    items = root.findall(".//item")
    print(f"\nTotal items in 2021-10 Gangnam: {len(items)}")
    
    for item in items:
        apt = item.findtext("아파트")
        if apt and "은마" in apt:
            area = item.findtext("전용면적")
            price = item.findtext("거래금액")
            print(f"Eunma match: Area={area}, Price={price}")
except Exception as e:
    print("Error:", e)
