with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

target = '''<div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div className="live-indicator"></div>
                    {complex.name}
                </div>'''

replacement = '''<div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1, minWidth: 0 }}>
                    <div className="live-indicator" style={{ flexShrink: 0 }}></div>
                    <div style={{ 
                        fontSize: complex.name.length > 10 ? '0.95rem' : (complex.name.length > 8 ? '1.05rem' : 'inherit'), 
                        whiteSpace: 'nowrap', 
                        overflow: 'hidden', 
                        textOverflow: 'ellipsis',
                        letterSpacing: complex.name.length > 8 ? '-1px' : 'inherit'
                    }}>
                        {complex.name}
                    </div>
                </div>'''

text = text.replace(target, replacement)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed long titles in ClientGrid')
