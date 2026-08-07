"""
50_naver_tx_type_audit.py (FINAL)
====================================================================
네이버 부동산 "시세/실거래가" 탭 내의 '타입 버튼'(예: 112A㎡)을 직접 클릭하여,
각 타입별 실거래가와 국토부 DB의 소수점 면적(exclusive_area_exact)을 매칭합니다.
이를 통해 기존의 잘못된 match_key_area 할당을 정밀 교정합니다.

[출력]
  pipeline/audit_report.json
  pipeline/pyeong_map_result.json (수정된 매칭 반영)
"""

import os, sys, io, time, re, json
from collections import defaultdict
from playwright.sync_api import sync_playwright

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

from dotenv import load_dotenv
from supabase import create_client, Client

env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
supabase: Client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_KEY'))

MAP_PATH = 'pipeline/pyeong_map_result.json'
REPORT_PATH = 'pipeline/audit_report.json'

# --- Utility Functions ---
def parse_price_cell(txt):
    """'32억 1(22일,39층)' -> (price, floor, day)"""
    txt = str(txt).strip()
    price_part = re.split(r'\(', txt)[0].strip()
    floor, day = None, None
    m = re.search(r'\(([^)]+)\)', txt)
    if m:
        inside = m.group(1)
        dm = re.search(r'(\d+)일', inside)
        fm = re.search(r'(\d+)층', inside)
        if dm: day = int(dm.group(1))
        if fm: floor = int(fm.group(1))
    p = price_part.replace(' ', '').replace(',', '')
    price = 0
    if '억' in p:
        parts = p.split('억')
        eok = int(parts[0]) * 100000000
        man_s = re.sub(r'[^0-9]', '', parts[1])
        price = eok + (int(man_s) * 10000 if man_s else 0)
    elif '만' in p:
        price = int(re.sub(r'[^0-9]', '', p)) * 10000
    return price, floor, day

def parse_date_cell(dt_raw, day=None):
    dt_raw = dt_raw.strip().rstrip('.')
    parts = dt_raw.split('.')
    if len(parts) >= 2:
        yy = '20' + parts[0] if len(parts[0]) == 2 else parts[0]
        mm = parts[1].zfill(2)
        if len(parts) >= 3 and parts[2]:
            dd = parts[2].zfill(2)
        elif day:
            dd = str(day).zfill(2)
        else:
            dd = '01'
        return f"{yy}-{mm}-{dd}"
    return None

def get_trades(complex_id):
    all_data, offset = [], 0
    while True:
        try:
            res = (supabase.table('rtms_transactions')
                   .select('deal_date,deal_price,floor,match_key_area,exclusive_area_exact')
                   .eq('complex_id', complex_id)
                   .order('deal_date', desc=True)
                   .range(offset, offset + 999)
                   .execute())
            batch = res.data or []
            all_data.extend(batch)
            if len(batch) < 1000: break
            offset += 1000
        except Exception as e:
            print(f"  [DB오류] Supabase 반환 대기 중 타임아웃 3초 대기 후 재시도... {e}")
            time.sleep(3)
            # 재시작 (offset 유지)
    return all_data

def find_db_match(trades, naver_txs):
    for tx in naver_txs:
        candidates = [t for t in trades if t['deal_date'] == tx['deal_date'] and t['deal_price'] == tx['deal_price']]
        if not candidates:
            # +- 1일 허용
            try:
                yy, mm, dd = tx['deal_date'].split('-')
                alt = [f"{yy}-{mm}-{str(int(dd)-1).zfill(2)}", f"{yy}-{mm}-{str(int(dd)+1).zfill(2)}"]
                candidates = [t for t in trades if t['deal_date'] in alt and t['deal_price'] == tx['deal_price']]
            except: pass
        if candidates:
            if tx['floor']:
                fl = [t for t in candidates if t.get('floor') == tx['floor']]
                if fl: return fl[0], 'date_price_floor'
            return candidates[0], 'date_price'
    return None, 'no_match'

# --- 메인 스크래퍼 ---
def scrape_type_txs(context, nid, target_ptp_names):
    """지정된 단지의 시세 탭에서, target_ptp_names에 해당하는 탭을 클릭해 거래들을 스크랩"""
    page = context.new_page()
    result = {}
    try:
        url = f"https://new.land.naver.com/complexes/{nid}?a=APT:ABYG:JGC&b=A1"
        page.goto(url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)

        # 1. 시세/실거래가 탭 클릭
        clicked = page.evaluate("""
            () => {
                const btns = Array.from(document.querySelectorAll('button.complex_data_button, button.complex_link, a.tab_item'));
                const btn = btns.find(b => b.innerText && b.innerText.includes('실거래가'));
                if(btn){ btn.click(); return true; }
                return false;
            }
        """)
        if not clicked:
            print(f"  [nid={nid}] '시세/실거래가' 탭 클릭 실패")
            return result
        time.sleep(2)

        # 2. 더보기 클릭
        try:
            page.locator("button.btn_moretab").first.click()
            time.sleep(1)
        except: pass

        # 3. 탭 클릭 및 데이터 수집
        for ptp_name in target_ptp_names:
            tab_text = f"{ptp_name}㎡"
            try:
                # 탭 찾아서 클릭
                tab_el = page.locator("a.detail_sorting_tab").filter(has_text=tab_text).first
                if not tab_el.is_visible():
                    tab_el = page.locator("a.detail_sorting_tab").filter(has_text=ptp_name).first
                tab_el.scroll_into_view_if_needed(timeout=2000)
                tab_el.click(force=True)
                time.sleep(1.5)

                rows = page.locator('.detail_data_table tbody tr').all()
                txs = []
                for row in rows[:7]:
                    try:
                        cells = row.locator('th, td').all()
                        if len(cells) < 2: continue
                        dt_raw, pr_raw = cells[0].inner_text().strip(), cells[1].inner_text().strip()
                        if '.' not in dt_raw or not pr_raw: continue
                        price, floor, day = parse_price_cell(pr_raw)
                        if price <= 0: continue
                        deal_date = parse_date_cell(dt_raw, day)
                        if deal_date:
                            txs.append({'deal_date': deal_date, 'deal_price': price, 'floor': floor})
                    except: continue
                result[ptp_name] = txs
                print(f"    [{tab_text}] {len(txs)}건 수집 완료")
            except Exception as e:
                print(f"    [{tab_text}] 탭 없음 혹은 오류")
                result[ptp_name] = []
        return result
    finally:
        page.close()

def run_audit():
    print("🚀 네이버 타입별 실거래가 감사 및 교정 시작...")
    
    with open(MAP_PATH, 'r', encoding='utf-8') as f:
        pyeong_map = json.load(f)
    with open('pipeline/naver_complex_mapping.json', 'r', encoding='utf-8') as f:
        nmap = json.load(f)

    complexes = supabase.table('complexes').select('*').execute().data
    cno_to_cid = {str(c['complex_no']): c['id'] for c in complexes}
    cid_to_name = {c['id']: c['name'] for c in complexes}

    nid_to_cid = {}
    for db_cno, nids in nmap.items():
        cid = cno_to_cid.get(str(db_cno))
        if not cid: continue
        for nid in ([nids] if isinstance(nids, str) else nids):
            nid_to_cid[str(nid)] = cid

    # nid -> ptp목록
    nid_groups = defaultdict(list)
    for node_key, entry in pyeong_map.items():
        if not isinstance(entry, dict) or 'nid' not in entry: continue
        nid_groups[str(entry['nid'])].append({
            'node_key': node_key,
            'ptp_no': str(entry['ptp_no']),
            'ptp_name': entry.get('ptp_name', ''),
            'old_mk': entry.get('match_key_area'),
            'ex_area': entry.get('exclusive_area', 0),
        })

    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, 'r', encoding='utf-8') as f:
            audit_report = json.load(f)
    else:
        audit_report = {}

    updated_map = dict(pyeong_map)
    total_audited = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for nid, ptps in nid_groups.items():
            cid = nid_to_cid.get(nid)
            if not cid: continue
            complex_name = cid_to_name.get(cid, f"nid={nid}")

            # 재시작 가능하도록 완료 체크
            if complex_name in audit_report and len(audit_report[complex_name]) == len(ptps):
                print(f"[SKIP] {complex_name}")
                continue

            print(f"\n{'='*60}")
            print(f"🏢 [{complex_name}] nid={nid} (총 {len(ptps)}타입)")

            rtms_trades = get_trades(cid)
            
            # ptp_names 추출
            target_ptps = [p['ptp_name'] for p in ptps if p['ptp_name']]
            
            # 스크래핑 (탭 클릭)
            naver_data = scrape_type_txs(context, nid, target_ptps)

            if complex_name not in audit_report:
                audit_report[complex_name] = {}

            # 매칭 및 교정
            for ptp in ptps:
                ptp_name = ptp['ptp_name']
                old_mk = ptp['old_mk']
                ex_area = ptp['ex_area']
                txs = naver_data.get(ptp_name, [])

                db_match, method = find_db_match(rtms_trades, txs)
                status = 'UNCHANGED'
                new_mk = old_mk
                actual_exact = None
                note = ""

                if db_match:
                    actual_exact = db_match.get('exclusive_area_exact')
                    new_mk = db_match.get('match_key_area')
                    print(f"  [{ptp_name}] 네이버 전용: {ex_area} -> DB 실제 전용: {actual_exact}")
                    
                    if new_mk and new_mk != old_mk:
                        status = 'FIXED'
                        note = f"{old_mk} -> {new_mk}"
                        print(f"    ✨ 교정 성공! {ptp_name} ㎡: {old_mk} -> {new_mk}")
                        updated_map[ptp['node_key']]['match_key_area'] = new_mk
                    else:
                        status = 'OK'
                else:
                    status = 'NO_DB_MATCH'
                    print(f"  [{ptp_name}] DB 매칭 실패")

                audit_report[complex_name][ptp_name] = {
                    'status': status,
                    'old_mk': old_mk,
                    'new_mk': new_mk,
                    'ptp_ex_area': ex_area,
                    'db_area_exact': actual_exact,
                    'note': note
                }
                total_audited += 1

            # 단지 끝날때마다 저장
            with open(REPORT_PATH, 'w', encoding='utf-8') as f:
                json.dump(audit_report, f, ensure_ascii=False, indent=2)
            with open(MAP_PATH, 'w', encoding='utf-8') as f:
                json.dump(updated_map, f, ensure_ascii=False, indent=2)

        context.close()
        browser.close()

    print(f"\n🎉 총 {total_audited}개 타입 감사 및 교정 완료!")

if __name__ == '__main__':
    run_audit()
