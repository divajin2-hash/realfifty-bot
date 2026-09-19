import re
text = open('dump.html', encoding='utf-8').read()
matches = re.finditer(r'"dealPrice"', text, re.IGNORECASE)
for m in list(matches)[:5]:
    print('dealPrice snippet:', text[max(0, m.start()-50):min(len(text), m.start()+300)])
