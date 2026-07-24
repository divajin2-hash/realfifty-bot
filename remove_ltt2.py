import re

def rebuild_sidebar_logo(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()

    new_sidebar = '''<div className="sidebar-logo" style={{ padding: '32px 24px 12px 24px' }}>
                    <div style={{ fontSize: '2.2rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px', textShadow: '0 2px 10px rgba(0,0,0,0.2)' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#76777d', letterSpacing: '2px', marginTop: '6px', fontWeight: 700 }}>
                        TERMINAL
                    </div>
                </div>'''

    # It's safer to just replace from <div className="sidebar-logo" to the end of that container.
    # We can match up to Real<span style={{ color: '#ffb4ab' }}>Fifty</span></div> plus the optional BY LANTERTAINER
    
    # Alternatively, just use string slice if we know what starts and ends it, but regex is fine with careful boundaries.
    # The container ends right before `<div style={{ padding: '0 24px', fontSize: '0.75rem', color: '#ffdad6', letterSpacing: '1px', fontWeight: 800, marginTop: '20px' }}>`
    # wait, we deleted the '최저점 모니터링' div!
    # So it is directly above `<div className="sidebar-menu" style={{ marginTop: '10px' }}>`
    
    pattern = r'<div className="sidebar-logo".*?(?=<div className="sidebar-menu")'
    text = re.sub(pattern, new_sidebar + '\n                ', text, flags=re.DOTALL)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(text)
    print('Updated Sidebar in', filepath)

rebuild_sidebar_logo('web/src/app/page.tsx')
rebuild_sidebar_logo('web/src/app/detail/[id]/page.tsx')
