import re

def rebuild_sidebar_logo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    # The current logo block might vary slightly in page.tsx and detail page due to padding, but I will replace between <div className="sidebar-logo"...> and BY LANTERTAINER</div></div>
    
    old_logo_pattern = r'<div className="sidebar-logo"[^>]*>.*?BY LANTERTAINER</div>\s*</div>'
    
    new_sidebar = '''<div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#76777d', letterSpacing: '2px', marginTop: '6px', fontWeight: 700 }}>
                        TERMINAL
                    </div>
                </div>'''

    if not re.search(old_logo_pattern, text, flags=re.DOTALL):
        # Fallback if the pattern doesn't match perfectly
        old_logo_pattern = r'<div className="sidebar-logo"[^>]*>.*?</div>\s*<div style={{ marginTop: \'20px\'[^>]*>.*?</div>\s*<div style={{[^>]*>.*?</div>\s*</div>'

    text = re.sub(old_logo_pattern, new_sidebar, text, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated Sidebar in', filepath)

rebuild_sidebar_logo('web/src/app/page.tsx')
rebuild_sidebar_logo('web/src/app/detail/[id]/page.tsx')
