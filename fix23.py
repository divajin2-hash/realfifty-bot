import re

with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix the absDrop (Real Transaction) Alert Box
old_alert_1 = r'''<div className="alert-box">\s*<div style=\{\{\s*fontSize:\s*'0\.65rem',\s*color:\s*'#ba1a1a',\s*whiteSpace:\s*'nowrap'\s*\}\}>고점대비 실거래</div>\s*\{absDrop === '0\.0' && absoluteRecent && absoluteRecent\.price \? \(\s*<div className="num-font" style=\{\{\s*marginTop:\s*'4px',\s*fontSize:\s*'1\.2rem',\s*fontWeight:\s*800\s*\}\}>최고가</div>\s*\)\s*:\s*\(\s*<div className="num-font" style=\{\{\s*marginTop:\s*'4px',\s*fontSize:\s*'1\.4rem'\s*\}\}>\{absDrop === '0\.0' \? '-' : `-\$\{absDrop\}%`\}</div>\s*\)\}\s*</div>'''

new_alert_1 = '''<div className="alert-box">
                        {absDrop === '0.0' && absoluteRecent && absoluteRecent.price ? (
                            <div style={{ paddingTop: '5px', fontSize: '1.2rem', fontWeight: 800, color: '#ba1a1a', whiteSpace: 'nowrap', textAlign: 'center' }}>최고가</div>
                        ) : (
                            <>
                                <div style={{ fontSize: '0.65rem', color: '#ba1a1a', whiteSpace: 'nowrap' }}>고점대비 실거래</div>
                                <div className="num-font" style={{ marginTop: '4px', fontSize: '1.4rem' }}>{absDrop === '0.0' ? '-' : `-${absDrop}%`}</div>
                            </>
                        )}
                    </div>'''

text = re.sub(old_alert_1, new_alert_1, text)

# 2. Fix the mddValue (Ask) Alert Box
old_alert_2 = r'''<div className="alert-box safe" style=\{\{\s*padding:\s*'8px 12px'\s*\}\}>\s*<div style=\{\{\s*fontSize:\s*'0\.6rem',\s*color:\s*'#131b2e',\s*opacity:\s*0\.8,\s*whiteSpace:\s*'nowrap'\s*\}\}>고점대비 호가</div>\s*\{mddValue === '0\.0' && currentAsk > 0 \? \(\s*<div className="num-font" style=\{\{\s*marginTop:\s*'2px',\s*fontSize:\s*'1\.1rem',\s*fontWeight:\s*800\s*\}\}>최고가</div>\s*\)\s*:\s*\(\s*<div className="num-font" style=\{\{\s*marginTop:\s*'2px',\s*fontSize:\s*'1\.2rem'\s*\}\}>\{mddValue === '0\.0' \? '-' : `\$\{mddValue\}%`\}</div>\s*\)\}\s*</div>'''

new_alert_2 = '''<div className="alert-box safe" style={{ padding: '8px 12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        {mddValue === '0.0' && currentAsk > 0 ? (
                            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#131b2e', whiteSpace: 'nowrap' }}>최고가</div>
                        ) : (
                            <div>
                                <div style={{ fontSize: '0.6rem', color: '#131b2e', opacity: 0.8, whiteSpace: 'nowrap', textAlign: 'right' }}>고점대비 호가</div>
                                <div className="num-font" style={{ marginTop: '2px', fontSize: '1.2rem' }}>{mddValue === '0.0' ? '-' : `${mddValue}%`}</div>
                            </div>
                        )}
                    </div>'''

text = re.sub(old_alert_2, new_alert_2, text)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated alert boxes!")
