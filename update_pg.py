import re
with open("web/src/app/page.tsx", "r", encoding="utf-8") as f:
    text = f.read()

# Replace signature
text = re.sub(r'export default async function Dashboard\(\) \{', 'export default async function Dashboard({ searchParams }: { searchParams: { sort?: string } }) {', text)

# Replace sort logic
old_sort_logic = '''    // 기획자님 지시: 화면에 노출되는 '대표평형' 기준으로 고점대비 실거래가가 가장 많이 빠진(하락률이 큰) 아파트순 정렬!
    groupedData.sort((a, b) => {
        const repA = getRepresentativeStat(a.stats);
        const repB = getRepresentativeStat(b.stats);

        // 유효하면 하락률 반환, 없으면 0. 가파른 폭락(마이너스 큼)이 1등
        const dropA = repA ? repA.recent_drop_rate : 0;
        const dropB = repB ? repB.recent_drop_rate : 0;

        return dropA - dropB; // 오름차순 (예: -38%가 -10%보다 먼저 배열)
    });'''

new_sort_logic = '''    const sortMethod = searchParams.sort || 'real_drop_high';
    
    // 정렬 방식 설정
    groupedData.sort((a, b) => {
        const repA = getRepresentativeStat(a.stats);
        const repB = getRepresentativeStat(b.stats);

        const realDropA = repA ? repA.recent_drop_rate : 0;
        const realDropB = repB ? repB.recent_drop_rate : 0;
        
        const askDropA = repA ? repA.mdd_rate : 0;
        const askDropB = repB ? repB.mdd_rate : 0;

        if (sortMethod === 'real_drop_less') {
            return realDropB - realDropA; // 실거래가 하락률 적은 순 (내림차순, 예: 0% -> -10% -> -30%)
        } else if (sortMethod === 'ask_drop_high') {
            return askDropA - askDropB; // 최저호가 하락률 높은 순 (오름차순, 예: -30% -> -10% -> 0%)
        } else if (sortMethod === 'ask_drop_less') {
            return askDropB - askDropA; // 최저호가 하락률 적은 순 (내림차순)
        } else {
            // 기본값: real_drop_high
            return realDropA - realDropB; // 실거래가 하락률 높은 순 (오름차순)
        }
    });'''

if old_sort_logic in text:
    text = text.replace(old_sort_logic, new_sort_logic)
else:
    print("Could not find old_sort_logic!")

with open("web/src/app/page.tsx", "w", encoding="utf-8") as f:
    f.write(text)
print("Updated page.tsx sorting logic!")
