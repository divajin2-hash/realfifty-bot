import re

with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add athDateStr
search_str = 'const absDrop = absoluteRecent'
replace_str = '''const athDateStr = activeStat.highest_deal_date ? `${activeStat.highest_deal_date.substring(2, 4)}.${activeStat.highest_deal_date.substring(5, 7)}.${activeStat.highest_deal_date.substring(8, 10)}` : '-';
  const absDrop = absoluteRecent'''
text = text.replace(search_str, replace_str)

# Replace label 1
old1 = '<span className="data-label">역대 최고가</span>'
new1 = '<span className="data-label">역대최고가 <span className="num-font" style={{fontSize: "0.85em", opacity: 0.6}}>({athDateStr})</span></span>'
text = text.replace(old1, new1)

# Replace label 2
old2 = '<span className="data-value-sub">최근 체결가: <span className="num-font">{absoluteRecent ? formatPriceNum(absoluteRecent.price) : \'-\'}</span><span className="kr-unit">억</span></span>'
new2 = '<span className="data-value-sub" style={{fontSize: "0.85rem"}}>최근 실거래 <span className="num-font" style={{fontSize: "0.9em", opacity: 0.75}}>({lastDealDateStr})</span> : <span className="num-font">{absoluteRecent ? formatPriceNum(absoluteRecent.price) : \'-\'}</span><span className="kr-unit">억</span></span>'
text = text.replace(old2, new2)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print('Patched ClientGrid.tsx!')
