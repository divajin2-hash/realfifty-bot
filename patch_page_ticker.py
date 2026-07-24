import re

with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Make sure to add import TickerClient
if "import TickerClient from './TickerClient'" not in text:
    text = text.replace("import ClientGrid from './ClientGrid'", "import ClientGrid from './ClientGrid'\nimport TickerClient from './TickerClient'")

old_ticker_re = r'const tickerElements = groupedData\.map.*?<React\.Fragment>.*?</React\.Fragment>\s*\);\n'
text = re.sub(old_ticker_re, '', text, flags=re.DOTALL)

old_div_re = r'<div className="top-ticker" style={{ overflow:.*?</style>\s*</div>'
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
text = re.sub(old_div_re, new_ticker.strip(), text, flags=re.DOTALL)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Patched page.tsx")
