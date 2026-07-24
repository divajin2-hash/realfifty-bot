import re

def remove_terminal(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    pattern = r'<div style={{ fontSize: \'0\.75rem\', color: \'#76777d\', letterSpacing: \'2px\', marginTop: \'6px\', fontWeight: 700 }}>\s*TERMINAL\s*</div>'
    
    text = re.sub(pattern, '', text, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Removed TERMINAL from', filepath)

remove_terminal('web/src/app/page.tsx')
remove_terminal('web/src/app/detail/[id]/page.tsx')
