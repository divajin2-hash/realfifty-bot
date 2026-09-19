with open('pipeline/11_api_scraper_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

import re
if 'sys.stdout.reconfigure' not in text:
    text = text.replace('import sys', 'import sys\nimport io\nsys.stdout.reconfigure(encoding=\"utf-8\")', 1)
    with open('pipeline/11_api_scraper_v2.py', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Patched 11_api script stdout")
