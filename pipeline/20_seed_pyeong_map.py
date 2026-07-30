import os
import json
from dotenv import load_dotenv
from supabase import create_client
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

load_dotenv('pipeline/.env')
supabase = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

def main():
    # 1. Load Naver raw asks to get all ptps
    with open('pipeline/raw_daily_asks_2026-07-28.json', 'r', encoding='utf-8') as f:
        asks = json.load(f)
        
    # Group Naver asks by complex_id (we need to map DB complex_id)
    with open('pipeline/naver_complex_mapping.json', 'r', encoding='utf-8') as f:
        nmap = json.load(f)
    rev_nmap = {v: k for k, v in nmap.items()}
    
    naver_by_cid = {}
    for ask in asks:
        cid = rev_nmap.get(ask['naver_complex_no'])
        if not cid: continue
        if cid not in naver_by_cid: naver_by_cid[cid] = {}
        ptp_no = ask['ptp_no']
        if ptp_no not in naver_by_cid[cid]:
            naver_by_cid[cid][ptp_no] = {
                'ptp_no': ptp_no,
                'ptp_name': ask['ptp_name'],
                'exclusive_area': ask['exclusive_area']
            }
            
    # 2. Get RTMS match_key_areas for all complexes
    rtms = supabase.table('rtms_transactions').select('complex_id, match_key_area').execute()
    rtms_by_cid = {}
    for r in rtms.data:
        cid = r['complex_id']
        if cid not in rtms_by_cid: rtms_by_cid[cid] = set()
        rtms_by_cid[cid].add(r['match_key_area'])
        
    print(f"Loaded {len(naver_by_cid)} complexes from Naver and {len(rtms_by_cid)} from RTMS.")
    
    for cid, n_ptps in naver_by_cid.items():
        if cid != 'dd976eb4-fbfd-4fce-acae-e043a72c21c9': continue
        print(f"\n--- Complex {cid} ---")
        rtms_areas = list(rtms_by_cid.get(cid, set()))
        rtms_areas.sort()
        print("RTMS Areas:", rtms_areas)
        print("Naver PTPs:")
        for ptp_no, n in n_ptps.items():
            print(f"  {n['ptp_name']} (No: {ptp_no}) - ExArea: {n['exclusive_area']}")
            
if __name__ == "__main__":
    main()
