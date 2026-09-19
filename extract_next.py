import re
import json

def repair_nextjs_json(text):
    # Extracts all strings that look like arrays with JSON strings in next.js format
    matches = re.finditer(r'\[[0-9]+,\"(.*?)\"\]', text)
    snippets = []
    for m in matches:
        raw_json_str = m.group(1).replace(r'\"', '"').replace(r'\\', '\\')
        if 'KB' in raw_json_str or 'marketPrice' in raw_json_str.lower() or '58' in raw_json_str:
            snippets.append(raw_json_str)
    return snippets

text = open('dump.html', encoding='utf-8').read()
results = repair_nextjs_json(text)
print(f"Found {len(results)} potential JSON chunks with KB or marketPrice")

with open('extracted_chunks.txt', 'w', encoding='utf-8') as f:
    for r in results:
        f.write(r + "\n====================\n")
