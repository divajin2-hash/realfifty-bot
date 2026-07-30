import requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
import sys; sys.stdout.reconfigure(encoding='utf-8')
key = unquote('QSuFJ4PDAimPWCOYd+Cqc6NWBW2kGOdP412a0lb68QuDEPLSc1I86Dcvi2hhkznSdf0e+BAxlr1RRsT+CdhUyw==')
r = requests.get('http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev', params={'serviceKey': key, 'LAWD_CD': '11710', 'DEAL_YMD': '202105', 'numOfRows': 3000})
root = ET.fromstring(r.content)
for item in root.findall('.//item'):
    apt = item.findtext('aptNm', '')
    if '주공' in apt and '5' in apt:
        print('Checking:', apt)
        if '직거래' in item.findtext('dealingGbn', ''): print('Failed dealingGbn'); continue
        if '잠실동' not in item.findtext('umdNm', ''): print('Failed umdNm', item.findtext('umdNm', '')); continue
        try:
            pr = int(item.findtext('dealAmount').replace(',','').strip()) * 10000
            ar = float(item.findtext('excluUseAr'))
            d = f"{item.findtext('dealYear')}-{int(item.findtext('dealMonth')):02d}-{int(item.findtext('dealDay')):02d}"
            f = int(item.findtext('floor'))
            print('Success!', pr, ar, d, f)
        except Exception as e:
            print('EXCEPTION:', e)
