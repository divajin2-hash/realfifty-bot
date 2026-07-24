import re

with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'<div className="top-ticker".*?</div>\s*<style dangerouslySetInnerHTML.*?</div>'
new_ticker = '''
                <TickerClient items={groupedData.map(g => {
                    const rep = getRepresentativeStat(g.stats);
                    return {
                        name: g.complex.name,
                        drop: rep ? rep.recent_drop_rate.toFixed(1) : "0.0",
                        isSevere: rep && rep.recent_drop_rate <= -20
                    };
                })} />
'''

text = re.sub(pattern, new_ticker.strip(), text, flags=re.DOTALL|re.IGNORECASE)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done fixing page.tsx")
