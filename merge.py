import re

# -------------
# COMPLEX MERGE
# -------------
with open('web/complex_old.tsx', 'r', encoding='utf-8') as f:
    old_complex = f.read()

with open('web/src/app/complex/page.tsx', 'r', encoding='utf-8') as f:
    new_complex_full = f.read()

# Extract tableData block from new_complex_full
table_data_match = re.search(r'(const tableData = rawData.*?)\n\s*const formatPrice', new_complex_full, re.DOTALL)
table_data_code = table_data_match.group(1) if table_data_match else ""

# Extract the JSX for the Header & Table from new_complex_full
jsx_match = re.search(r'(<div className="desktop-only".*?단지 시세 보드 \(COMPLEX MATRIX\).*?</table>\s*</div>\s*</div>\s*<div className="num-font".*?</div>)', new_complex_full, re.DOTALL)
table_jsx = jsx_match.group(1) if jsx_match else ""

# Insert tableData logic into old complex
old_complex = old_complex.replace('const rep = complexObj.stats.find((s: any) => true);', f'const rep = complexObj.stats.find((s: any) => true);\n\n    {table_data_code}\n    const formatPrice = (p: number) => p > 0 ? (p / 100000000).toFixed(1) + "억" : "-";')

# Insert table JSX into old complex right after {/* 1. Header Area */} div closed
insertion_point = '{/* 2. Complex Detail Header */}'
old_complex = old_complex.replace(insertion_point, f'{table_jsx}\n\n                <div style={{{{ marginTop: "60px", marginBottom: "32px", borderBottom: "1px solid var(--border-light)" }}}}></div>\n\n                {insertion_point}')

with open('web/src/app/complex/page.tsx', 'w', encoding='utf-8') as f:
    f.write(old_complex)


# -------------
# MARKET MERGE
# -------------
with open('web/market_old.tsx', 'r', encoding='utf-8') as f:
    old_market = f.read()

with open('web/src/app/market/page.tsx', 'r', encoding='utf-8') as f:
    new_market_full = f.read()

# Extract groupedData calculation
group_data_match = re.search(r'(const groupedData = rawData\.map.*?const scatterPoints = groupedData;)', new_market_full, re.DOTALL)
group_data_code = group_data_match.group(1) if group_data_match else ""

# Extract real 4-Quadrant mapping block completely! 
matrix_match = re.search(r'(<div style=\{\{ display: \'grid\', gridTemplateColumns: \'minmax\(0, 1.8fr\) minmax\(0, 1fr\)\'.*?4분면 매트릭스 리딩 가이던스.*?</div>\s*</div>\s*</div>)', new_market_full, re.DOTALL)
matrix_jsx = matrix_match.group(1) if matrix_match else ""

# Replace old groupedData logic (if exists) or just insert it
if 'const groupedData =' in old_market:
    old_market = re.sub(r'const groupedData = .*?const scatterPoints = .*?;', group_data_code, old_market, flags=re.DOTALL)
else:
    # insert after rawData try block
    old_market = old_market.replace("try { rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8')); } catch (e) { }", "try { rawData = JSON.parse(fs.readFileSync(jsonPath, 'utf8')); } catch (e) { }\n\n" + group_data_code)

# Replace the OLD Market Map section with the NEW one
old_market = re.sub(r'<\!-- REALFIFTY MARKET MAP 4분면 매트릭스 -->.*?(?:{/\* 4\. REALFIFTY MARKET MAP.*?)<div style=\{\{ display: \'grid\', gridTemplateColumns: \'minmax\(0, 1\.8fr\).*?</div>\s*</div>\s*</div>', matrix_jsx, old_market, flags=re.DOTALL)

# Wait, regex for the old market map is tricky. Let's just find the starting tag and replacing down to the end of that grid
old_market = re.sub(r'\{\/\*\s*4\.\s*REALFIFTY MARKET MAP.*?</div>\s*</div>\s*</div>', matrix_jsx, old_market, flags=re.DOTALL)

with open('web/src/app/market/page.tsx', 'w', encoding='utf-8') as f:
    f.write(old_market)

print("Merged successfully!")
