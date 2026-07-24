def patch_client_grid():
    with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Update ComplexCard signature
    text = text.replace('function ComplexCard({ complex, stats }: { complex: any, stats: any[] }) {', 
                        'function ComplexCard({ complex, stats, rank }: { complex: any, stats: any[], rank: number }) {')

    # 2. Add rank div manually using standard replace with split
    import re
    old_header_pattern = r'<div className="card-header-navy">.*?</div>\s*</div>\s*</div>'
    new_header = '''<div className="card-header-navy">
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div className="live-indicator"></div>
                    {complex.name}
                </div>
                <div style={{ background: '#ffb4ab', color: '#ba1a1a', padding: '4px 8px', borderRadius: '4px', fontSize: '0.85rem', fontWeight: 900 }}>
                    {rank}위
                </div>
            </div>'''
    text = re.sub(old_header_pattern, new_header.replace('\\', '\\\\'), text, flags=re.DOTALL)

    # 3. Handle ClientGrid function
    idx = text.find('export default function ClientGrid')
    if idx != -1:
        text = text[:idx] + '''export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
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
                {filtered.map((group) => (
                    <ComplexCard key={group.complex.id} complex={group.complex} stats={group.stats} rank={group.rank} />
                ))}
                {filtered.length === 0 && (
                    <div style={{ gridColumn: '1 / -1', padding: '60px', textAlign: 'center', color: '#76777d', fontSize: '1.2rem', fontWeight: 700 }}>
                        검색 결과가 없습니다.
                    </div>
                )}
            </div>
        </div>
    );
}'''
    
    with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print('Patched ClientGrid.tsx completely!')

patch_client_grid()
