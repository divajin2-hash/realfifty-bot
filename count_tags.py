with open('web/src/app/market/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

div_start = text.count('<div ') + text.count('<div>')
div_end = text.count('</div>')

print(f"div tags: {div_start}")
print(f"</div> tags: {div_end}")

if div_start != div_end:
    print(f"Mismatch! Unclosed divs: {div_start - div_end}")
