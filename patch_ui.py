import re

# 1. Patch page.tsx
with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    page_text = f.read()

ticker_code = '''
    const tickerElements = groupedData.map((g, idx) => {
        const rep = getRepresentativeStat(g.stats);
        const drop = rep ? rep.recent_drop_rate.toFixed(1) : "0.0";
        const isSevere = rep && rep.recent_drop_rate <= -20;
        return (
            <span key={idx} style={{ marginRight: '50px', fontSize: '0.95rem' }}>
                <strong style={{ fontWeight: 800 }}>{g.complex.name}</strong> 
                <span className="num-font" style={{ color: isSevere ? '#ffb4ab' : '#ffffff', marginLeft: '8px', fontWeight: 800, textShadow: isSevere ? '0 0 10px rgba(255,180,171,0.5)' : 'none' }}>
                    {drop}%
                </span>
            </span>
        );
    });

    const TickerContent = () => (
        <React.Fragment>
            {tickerElements}{tickerElements}
        </React.Fragment>
    );
'''

# Use replacement
page_text = page_text.replace('    return (', ticker_code + '\n    return (')

old_ticker_re = r'<div className="top-ticker">.*?</div>'
new_ticker = '''<div className="top-ticker" style={{ overflow: 'hidden', whiteSpace: 'nowrap', position: 'relative', display: 'flex', alignItems: 'center' }}>
                    <div style={{ display: 'inline-block', animation: 'marquee 80s linear infinite' }}>
                        <TickerContent />
                    </div>
                    <style dangerouslySetInnerHTML={{__html: `
                        @keyframes marquee {
                            0% { transform: translateX(0); }
                            100% { transform: translateX(-50%); }
                        }
                    `}} />
                </div>'''
page_text = re.sub(old_ticker_re, new_ticker, page_text, flags=re.DOTALL)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(page_text)
print('Patched page.tsx')

# 2. Patch ClientGrid.tsx
with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    grid_text = f.read()

old_grid_head = '''export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
  return (
    <div className="grid-layout">'''

new_grid_head = '''export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
  const [searchQuery, setSearchQuery] = useState("");
  
  const filtered = groupedData.filter(g => g.complex.name.replace(/\\s+/g, '').includes(searchQuery.replace(/\\s+/g, '')));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '24px', marginTop: '-15px' }}>
         <div style={{ position: 'relative', width: '300px' }}>
            <span style={{ position: 'absolute', left: '16px', top: '12px', opacity: 0.5 }}>🔍</span>
            <input 
              type="text" 
              placeholder="단지명 검색 (예: 은마, 래미안)" 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%', padding: '12px 16px 12px 42px', borderRadius: '30px', border: '1px solid #e0e3e6', background: 'white', fontSize: '0.95rem', fontWeight: 600, outline: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.03)' }}
            />
         </div>
      </div>
      <div className="grid-layout">
        {filtered.length === 0 && (
            <div style={{ gridColumn: '1 / -1', padding: '60px', textAlign: 'center', color: '#76777d', fontSize: '1.2rem', fontWeight: 700 }}>
                검색 결과가 없습니다.
            </div>
        )}'''

grid_text = grid_text.replace(old_grid_head, new_grid_head)

old_grid_tail = '''    </div>
  );
}'''
new_grid_tail = '''    </div>
    </div>
  );
}'''
if new_grid_tail not in grid_text:
    grid_text = grid_text.replace(old_grid_tail, new_grid_tail)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(grid_text)
print('Patched ClientGrid.tsx')
