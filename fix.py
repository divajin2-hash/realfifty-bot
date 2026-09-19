import re

with open('web/src/app/news/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(r'\"[^\"]+빙하기 진입\"', '"{leadNews.body_summary}"', text)
text = re.sub(r'<ul style={{ color:.*?</ul>', '', text, flags=re.DOTALL)
text = re.sub(r'데이터 결론:.*?과장 프레임\.', '{leadNews.factcheck_content}', text, flags=re.DOTALL)

with open('web/src/app/news/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

print("done")
