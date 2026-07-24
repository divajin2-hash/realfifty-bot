import re

def patch_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        pattern_lowest_point = r'<div style={{[^}]*}}>\s*최저점 모니터링\s*</div>'
        text = re.sub(pattern_lowest_point, '', text)
        
        text = text.replace('전국 대장주 50선 모니터링', '선도50 아파트 모니터링')
        text = text.replace('전국 대장주 50선', '선도50 아파트')
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print('Updated', filepath)
    except Exception as e:
        print('Error in', filepath, e)

patch_file('web/src/app/page.tsx')
patch_file('web/src/app/detail/[id]/page.tsx')
