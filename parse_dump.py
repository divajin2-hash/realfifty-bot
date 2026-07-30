import bs4
with open('dump.html', encoding='utf-8') as f:
    text = f.read()
soup = bs4.BeautifulSoup(text, 'html.parser')
res = []
for el in soup.find_all(lambda t: t.name in ['button', 'a', 'span'] and any(x in t.text for x in ['가격', '관련도'])):
    res.append(f"TAG: {el.name}, CLASS: {el.get('class')}, TEXT: {el.text.strip()}")
with open('parsed.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(res))
