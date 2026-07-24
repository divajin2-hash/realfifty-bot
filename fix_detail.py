import re

def fix_detail():
    with open('web/src/app/detail/[id]/page.tsx', 'r', encoding='utf-8') as f:
        text = f.read()

    # The exact block based on lines 47-58:
    idx = text.find('const [activeIndex, setActiveIndex] = useState(() => getRepIndex(sortedStats));')
    idx_end = text.find('const activeStat = sortedStats[activeIndex];')

    if idx != -1 and idx_end != -1:
        prefix = text[:idx]
        suffix = text[idx_end:]
        
        new_block = '''const group = (rawData as any[]).find(g => g.complex.id === complexId);
    
    const sortedStats = group ? [...group.stats].map(s => {
        const mdd_rate = s.highest_deal_price > 0 ? -Math.abs(((s.highest_deal_price - s.current_lowest_ask) / s.highest_deal_price) * 100) : 0;
        return { ...s, mdd_rate };
    }).sort((a, b) => a.match_key_area - b.match_key_area) : [];

    const [activeIndex, setActiveIndex] = useState(() => getRepIndex(sortedStats));

    if (!group) return <div style={{ padding: '50px' }}>단지를 찾을 수 없습니다.</div>;
    const complex = group.complex;

    '''
        new_text = prefix + new_block + suffix
        with open('web/src/app/detail/[id]/page.tsx', 'w', encoding='utf-8') as f:
            f.write(new_text)
        print('Fixed detail page hooks order!!')
    else:
        print('Could not find the block to replace')

fix_detail()
