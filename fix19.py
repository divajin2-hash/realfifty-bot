with open('pipeline/19_build_json_db.py', 'r', encoding='utf-8') as f:
    text = f.read()
text = text.replace('c["address"]', 'c.get("region", "")')
text = text.replace('trades_sorted[-3:]', 'trades_sorted[-5:]')
with open('pipeline/19_build_json_db.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("done")
