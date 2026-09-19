with open('web/src/app/market/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    )\n}', '            </div>\n        </div>\n    )\n}')

with open('web/src/app/market/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
