import re

with open('web/src/app/news/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove the whole debug div
text = re.sub(r'\{\!leadNews && \(\s*<div style=\{\{ color: \'red\'.*?</div>\s*\)\}', '', text, flags=re.DOTALL)

with open('web/src/app/news/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
