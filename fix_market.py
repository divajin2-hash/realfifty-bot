with open('web/src/app/market/page.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if line.strip() == "const scatterPoints = groupedData;":
        new_lines.append(line)
        skip = True
        continue
    
    if skip:
        if "return (" in line:
            skip = False
            new_lines.append(line)
        continue
        
    new_lines.append(line)

with open('web/src/app/market/page.tsx', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("done")
