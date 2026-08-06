import os

with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<div className="menu-item active">?? 실시간 시장 현황</div>', '<Link href="/" style={{textDecoration:\'none\', color:\'inherit\'}}><div className="menu-item active">📈 실시간 시장 현황</div></Link>')
content = content.replace('<div className="menu-item">?? 거래량 추이 통계</div>', '<Link href="/market" style={{textDecoration:\'none\', color:\'inherit\'}}><div className="menu-item">📊 종합 시황 현황</div></Link>')
content = content.replace('<Link href="/reports" style={{ textDecoration: \'none\', color: \'inherit\' }}><div className="menu-item">?? 종합 마켓 리포트</div></Link>\n', '')
content = content.replace('<div className="menu-item">?? 급매물 알림</div>', '<div className="menu-item">🚨 급매물 알림</div>')
content = content.replace('<div className="menu-item">?? 관심 단지 등록</div>', '<div className="menu-item">⭐ 관심 단지 등록</div>')

# Also remove the MacroIndexChart from the main page directly if we create a /market page
# Wait, I won't remove it yet until we actually build /market.

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
