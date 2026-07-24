import re

# 1. Patch page.tsx
with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace Sidebar Logo
old_sidebar_logo = r'<div className="sidebar-logo">\s*전문가용 터미널\s*</div>'
new_sidebar_logo = '''<div className="sidebar-logo" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '30px 20px 10px 20px' }}>
                    <div style={{ background: '#ffffff', padding: '16px 12px', borderRadius: '12px', width: '100%', display: 'flex', justifyContent: 'center', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
                        <img src="/logo.png" alt="LANTERTAINER" style={{ maxWidth: '100%', maxHeight: '50px', objectFit: 'contain' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />
                    </div>
                    <div style={{ marginTop: '20px', fontSize: '1.8rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px' }}>
                        Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#76777d', letterSpacing: '2px', marginTop: '4px' }}>BY LANTERTAINER</div>
                </div>'''

text = re.sub(old_sidebar_logo, new_sidebar_logo, text, flags=re.DOTALL)

# Replace Dashboard Title
old_h1 = r'<h1 style={{ fontSize: \'2.5rem\', fontWeight: 800, letterSpacing: \'-1px\' }}>전국 대장주 50선 모니터링</h1>'
new_h1 = '''<h1 style={{ fontSize: '2.5rem', fontWeight: 800, letterSpacing: '-1px' }}>
                                <span style={{color: '#ba1a1a', marginRight: '12px'}}>RealFifty</span> 
                                전국 대장주 50선 모니터링
                            </h1>'''
text = text.replace(old_h1, new_h1)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched page.tsx')

# 2. Patch detail/[id]/page.tsx
with open('web/src/app/detail/[id]/page.tsx', 'r', encoding='utf-8') as f:
    detail_text = f.read()

old_detail_logo = r'<div className="sidebar-logo" style={{fontSize: \'1.2rem\', padding: \'24px\'}}>전문가용 터미널</div>'
new_detail_logo = '''<div className="sidebar-logo" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '30px 20px 10px 20px' }}>
          <div style={{ background: '#ffffff', padding: '12px', borderRadius: '12px', width: '100%', display: 'flex', justifyContent: 'center' }}>
              <img src="/logo.png" alt="LANTERTAINER" style={{ maxWidth: '100%', maxHeight: '40px', objectFit: 'contain' }} onError={(e) => { e.currentTarget.style.display = 'none'; }} />
          </div>
          <div style={{ marginTop: '20px', fontSize: '1.4rem', fontWeight: 900, color: '#ffffff', letterSpacing: '1px' }}>
              Real<span style={{ color: '#ffb4ab' }}>Fifty</span>
          </div>
        </div>'''
detail_text = detail_text.replace(old_detail_logo, new_detail_logo)

old_detail_title = r'<h1 style={{fontSize: \'4rem\', color: \'rgba(0,0,0,0.04)\', fontWeight: 800, letterSpacing: \'4px\'}}>MDD TERMINAL ANALYTICS</h1>'
new_detail_title = r'<h1 style={{fontSize: \'4.5rem\', color: \'rgba(0,0,0,0.04)\', fontWeight: 800, letterSpacing: \'4px\'}}>REALFIFTY ANALYTICS</h1>'
detail_text = detail_text.replace(old_detail_title, new_detail_title)

with open('web/src/app/detail/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(detail_text)
print('Patched detail/[id]/page.tsx')
