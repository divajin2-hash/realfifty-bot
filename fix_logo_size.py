def change_logo_size(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = text.replace("maxHeight: '50px'", "maxHeight: '85px'")
    text = text.replace("maxHeight: '40px'", "maxHeight: '75px'")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated image size in', filepath)

change_logo_size('web/src/app/page.tsx')
change_logo_size('web/src/app/detail/[id]/page.tsx')
