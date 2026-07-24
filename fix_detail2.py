import re

with open('web/src/app/detail/[id]/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Sidebar Links
old_sidebar = r'<div className="menu-item" onClick=\{\(\) => router.push\(\'/\'\)\}>.*?</div>\s*<div className="menu-item active">.*?</div>\s*<div className="menu-item">.*?</div>\s*<div className="menu-item">.*?</div>'
new_sidebar = '''<div className="menu-item" onClick={() => router.push('/')}>📊 실시간 시장 현황 (메인)</div>
                    <div className="menu-item active">📊 통합 마켓 상세 현황</div>
                    <div className="menu-item">🔔 가격 변동 알림 (준비중)</div>
                    <div className="menu-item">💼 관심 단지 등록 (준비중)</div>'''
text = re.sub(old_sidebar, new_sidebar, text, flags=re.DOTALL)

# Also fix the text replacement if the above regex failed:
text = text.replace('<div className="menu-item" onClick={() => router.push(\'/\')}>📊 실시간 하락장 분석</div>', '<div className="menu-item" onClick={() => router.push(\'/\')}>📊 실시간 시장 현황 (메인)</div>')

# 2. Add TickerClient Import
if 'import TickerClient' not in text:
    text = text.replace("import rawData from '@/data/kb50_stats.json';", "import rawData from '@/data/kb50_stats.json';\nimport TickerClient from '../../TickerClient';")

# 3. Replace Static Ticker
old_ticker_pattern = r'<div className="top-ticker".*?</div>'
new_ticker = '''<div className="top-ticker" style={{ padding: 0, overflow: 'hidden' }}>
                    <TickerClient items={(() => {
                        const totalDropRates = (rawData as any[]).map(g => {
                            const rep = getRepresentativeStat(g.stats);
                            return rep ? rep.recent_drop_rate : 0;
                        }).filter(d => d < 0);
                        const avgNum = totalDropRates.length > 0 
                            ? parseFloat((totalDropRates.reduce((acc, val) => acc + val, 0) / totalDropRates.length).toFixed(2)) 
                            : 0;

                        const groupedDataForTicker = [...(rawData as any[])].map(g => {
                            const rep = getRepresentativeStat(g.stats);
                            return {
                                name: g.complex.name,
                                recent_drop_rate: rep ? rep.recent_drop_rate : 0
                            };
                        }).sort((a,b) => a.recent_drop_rate - b.recent_drop_rate);
                        
                        groupedDataForTicker.forEach((g, idx) => g.rank = idx + 1);

                        return groupedDataForTicker
                            .filter(item => item.recent_drop_rate < avgNum)
                            .map(item => ({
                                name: item.name,
                                drop: item.recent_drop_rate.toFixed(1),
                                isSevere: item.recent_drop_rate <= -20,
                                rank: item.rank
                            }));
                    })()} />
                </div>'''

# Need to accurately match up to the closing div of top-ticker
# Wait, old_ticker_pattern could match too much. let's just find <div className="top-ticker"> and swap it explicitly.
idx1 = text.find('<div className="top-ticker">')
if idx1 != -1:
    idx2 = text.find('</div>', idx1)
    text = text[:idx1] + new_ticker + text[idx2+6:]


# 4. Remove X'd out elements
# user sketch #3: remove red bubble "유동성 시그널 현황" entirely and just leave the top part.
text = re.sub(r'<div style=\{\{ fontSize: \'0\.8rem\', color: \'#191c1e\', fontWeight: 700 \}\}>유동성 시그널 현황</div>.*?역대 최대 거래월 대비 급감</span>\s*</div>', '', text, flags=re.DOTALL)

# user sketch: remove red bubble "고점 대비 수익률 하락 -X%"
text = re.sub(r'<div className="alert-box-danger" style=\{\{ display: \'flex\', justifyContent: \'space-between\', alignItems: \'center\', marginTop: \'16px\' \}\}>\s*<span className="num-font">\{-mdd_rate\}%</span>\s*<span style=\{\{ fontSize: \'0\.75rem\', opacity: 0\.8 \}\}>고점 대비 수익률 하락</span>\s*</div>', '', text, flags=re.DOTALL)


# 5. Format gap text
text = re.sub(r'최근 실거래가 대비 장부상 <span className="num-font"[\s\S]*?반등 호가\.', '''{(() => {
                                    const gap = currentAsk - (absoluteRecent ? absoluteRecent.price : 0);
                                    if (!absoluteRecent) return '최근 실거래 없음';
                                    const gapEok = Math.abs(gap / 100000000).toFixed(1);
                                    if (gap < 0) return `최근 실거래가 대비 ${gapEok}억원 저렴`;
                                    if (gap > 0) return `최근 실거래가 대비 ${gapEok}억원 비쌈`;
                                    return `최근 실거래가와 동일`;
                                })()}''', text, flags=re.DOTALL)


with open('web/src/app/detail/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Applied UI tweaks for Detail page.')
