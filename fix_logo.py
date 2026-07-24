def change_logo_path(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    new_text = text.replace('src="/logo.png"', 'src="/ltt.png"')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print('Updated image path in', filepath)

change_logo_path('web/src/app/page.tsx')
change_logo_path('web/src/app/detail/[id]/page.tsx')
