with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix NaN when ath is 0
text = text.replace("const absDrop = absoluteRecent ? (((ath - absoluteRecent.price) / ath) * 100).toFixed(1) : '0.0';", "const absDrop = (absoluteRecent && ath > 0 && absoluteRecent.price) ? (((ath - absoluteRecent.price) / ath) * 100).toFixed(1) : '0.0';")

# Graceful representation if ath date is broken or missing
text = text.replace("const athDateStr = activeStat.highest_deal_date ? `${activeStat.highest_deal_date.substring(2, 4)}.${activeStat.highest_deal_date.substring(5, 7)}.${activeStat.highest_deal_date.substring(8, 10)}` : '-';", 
"const athDateStr = activeStat.highest_deal_date && activeStat.highest_deal_date.length >= 10 ? `${activeStat.highest_deal_date.substring(2, 4)}.${activeStat.highest_deal_date.substring(5, 7)}.${activeStat.highest_deal_date.substring(8, 10)}` : '-';")

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(text)

with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    ptext = f.read()
    
ptext = ptext.replace("const recent_drop_rate = s.highest_deal_price > 0 ? -Math.abs(((s.highest_deal_price - recentPrice) / s.highest_deal_price) * 100) : 0;", 
"const recent_drop_rate = (s.highest_deal_price > 0 && recentPrice) ? -Math.abs(((s.highest_deal_price - recentPrice) / s.highest_deal_price) * 100) : 0;")

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(ptext)
print('Fixed NaNs')
