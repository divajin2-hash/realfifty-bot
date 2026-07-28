import os, sys, requests, xml.etree.ElementTree as ET
from urllib.parse import unquote
import json
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
if not url or not key: sys.exit(0)
sb = create_client(url, key)
molit_key = unquote(os.environ.get("RTMS_API_KEY"))

# Wipe existing corrupted trades for both
cid_1_5 = '94379391-ef97-4ce2-a4a1-bcb00a070ba7'
cid_shin = 'dd976eb4-fbfd-4fce-acae-e043a72c21c9'

sb.table('rtms_transactions').delete().in_('complex_id', [cid_1_5, cid_shin]).execute()

aliases = {
    cid_1_5: ["현대1,2차", "현대3차", "현대4차", "현대5차", "현대1차", "현대2차", "압구정현대1차"],
    cid_shin: ["현대", "현대9차", "현대11차", "현대12차", "신현대", "현대(신현대)", "현대아파트"]
}

def clean_name(n):
    return n.replace("(", "").replace(")", "").replace(" ", "").strip()

def get_cid(api_name):
    ci = clean_name(api_name)
    for cid, alist in aliases.items():
        if ci == clean_name(cid): return cid
        for al in alist:
            if ci == clean_name(al):
                return cid
    return None

def format_price(p_str):
    try: return int(p_str.replace(",", "").strip()) * 10000
    except: return 0

ins_count = 0
for year in [2023, 2024, 2025, 2026]:
    for month in range(1, 13):
        ym = f"{year}{month:02d}"
        if ym > "202607": break
        
        req_url = 'http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev'
        params = {'serviceKey': molit_key, 'LAWD_CD': '11680', 'DEAL_YMD': ym}
        r = requests.get(req_url, params=params)
        
        try:
            root = ET.fromstring(r.content)
            for item in root.findall('.//item'):
                aptNm = item.findtext('aptNm')
                c_id = get_cid(aptNm)
                if c_id:
                    price = format_price(item.findtext('dealAmount'))
                    area = float(item.findtext('excluUseAr'))
                    floor = item.findtext('floor')
                    day = item.findtext('dealDay')
                    dy = f"{year}-{month:02d}-{int(day):02d}"
                    t_type = item.findtext('reqGbn')
                    
                    sb.table('rtms_transactions').insert({
                        "complex_id": c_id,
                        "deal_price": price,
                        "match_key_area": int(round(area)),
                        "exclusive_area_exact": area,
                        "deal_date": dy,
                        "floor": int(floor) if floor and floor.strip('-').isdigit() else None,
                        "transaction_type": t_type
                    }).execute()
                    ins_count += 1
        except Exception as e:
            pass

print("Healed! Inserted:", ins_count)
