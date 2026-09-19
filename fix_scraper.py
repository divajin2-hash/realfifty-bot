import re

with open('pipeline/11_api_scraper_v2.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('if sale_count == 0 and jeonse_count == 0: continue', '# if sale_count == 0 and jeonse_count == 0: continue # Changed: Keep empty property types')

with open('pipeline/11_api_scraper_v2.py', 'w', encoding='utf-8') as f:
    f.write(text)
