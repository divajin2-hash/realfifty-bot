import re

with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the TickerClient call to include filtering and rank calculation
old_ticker_client_re = r'<TickerClient\s+items=\{groupedData\.map\(g =>\s*\{.*?\}\)\}\s*/>'

# Calculate average drop value and filter items
new_ticker_client = '''
                <TickerClient items={(() => {
                    const avgNum = parseFloat(avgDrop);
                    const items = groupedData.map(g => {
                        const rep = getRepresentativeStat(g.stats);
                        return {
                            name: g.complex.name,
                            rawDrop: rep ? rep.recent_drop_rate : 0,
                            drop: rep ? rep.recent_drop_rate.toFixed(1) : "0.0",
                            isSevere: rep && rep.recent_drop_rate <= -20,
                            rank: 0
                        };
                    });
                    
                    // Filter: Only include items whose drop is WORSE (more negative) than the average drop
                    const filtered = items.filter(item => item.rawDrop < avgNum);
                    
                    // Assign explicit ranking (since groupedData is already sorted)
                    filtered.forEach((item, idx) => {
                        item.rank = idx + 1;
                    });
                    
                    return filtered;
                })()} />
'''

text = re.sub(old_ticker_client_re, new_ticker_client.strip(), text, flags=re.DOTALL)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched page.tsx")
