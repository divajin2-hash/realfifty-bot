with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = '''<div className="num-font" style={{ marginTop: '4px', fontSize: '1.4rem' }}>{-absDrop}%</div>'''
replacement1 = '''{absDrop === '0.0' && absoluteRecent && absoluteRecent.price ? (
                            <div className="num-font" style={{ marginTop: '4px', fontSize: '1.2rem', fontWeight: 800 }}>최고가</div>
                        ) : (
                            <div className="num-font" style={{ marginTop: '4px', fontSize: '1.4rem' }}>{absDrop === '0.0' ? '-' : `-${absDrop}%`}</div>
                        )}'''
text = text.replace(target1, replacement1)

target2 = '''<div className="num-font" style={{ marginTop: '2px', fontSize: '1.2rem' }}>{mddValue}%</div>'''
replacement2 = '''{mddValue === '0.0' && currentAsk > 0 ? (
                            <div className="num-font" style={{ marginTop: '2px', fontSize: '1.1rem', fontWeight: 800 }}>최고가</div>
                        ) : (
                            <div className="num-font" style={{ marginTop: '2px', fontSize: '1.2rem' }}>{mddValue === '0.0' ? '-' : `${mddValue}%`}</div>
                        )}'''
text = text.replace(target2, replacement2)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("done replacing")
