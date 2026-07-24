import json
import re

with open('pipeline/19_build_json_db.py', 'r', encoding='utf-8') as f:
    text = f.read()

# I want to replace the current_lowest_ask heuristic with a slightly smarter one that takes the median or max of the last 3 deals.
old_heuristic = '            "current_lowest_ask": int(absolute_recent["deal_price"] * 0.98)'
new_heuristic = '''            # Smart Heuristic: Average of the last 3 trades * 0.98 (to avoid single anomaly dropping the ask price too much)
            recent_3_trades = trades_sorted[-3:]
            avg_recent = sum(t["deal_price"] for t in recent_3_trades) / len(recent_3_trades)
            "current_lowest_ask": int(avg_recent * 0.98)'''

# Regex string matching might be easier for CP949 resilient replacement
def replace_heuristic():
    lines = text.split('\\n')
    for i, line in enumerate(lines):
        if '"current_lowest_ask": int(absolute_recent["deal_price"]' in line:
            lines[i] = '''            "current_lowest_ask": int((sum(t["deal_price"] for t in trades_sorted[-3:]) / len(trades_sorted[-3:])) * 0.98) # API 막힘 방지용 보정(최근3개평균)'''
    
    with open('pipeline/19_build_json_db.py', 'w', encoding='utf-8') as out:
        out.write('\\n'.join(lines))
    print('Updated pipeline 19 heuristic!')

replace_heuristic()
