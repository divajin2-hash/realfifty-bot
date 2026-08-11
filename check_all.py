import json

def check_all():
    with open('web/src/data/kb50_stats.json', encoding='utf-8') as f:
        db = json.load(f)
        
    zero_ptps = []
    
    for c in db:
        cx_name = c['complex']['name']
        for s in c['stats']:
            if len(s['all_trades_history']) == 0:
                zero_ptps.append((cx_name, s['pyeong_name'], s['match_key_area']))
                
    print(f'Found {len(zero_ptps)} 0-trade types.')
    for cx in sorted(set(x[0] for x in zero_ptps)):
        print(f"{cx}: {[x[1] for x in zero_ptps if x[0] == cx]}")

if __name__ == '__main__':
    check_all()
