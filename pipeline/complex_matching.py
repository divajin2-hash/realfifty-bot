import re

# Preserve phase numbers: removing parenthesis contents conflates separate complexes.
ALIASES = {
    '디에이치퍼스티어아이파크': ['디에이치퍼스티어아이파크'],
    '현대(신현대)': ['신현대9차', '신현대11차', '신현대12차'],
    '현대(6 7차)': ['현대6차', '현대7차'],
    '현대(1~5차)': ['현대1차', '현대2차', '현대3차', '현대4차저층', '현대5차'],
    '한보미도맨션': ['한보미도맨션1', '한보미도맨션2'],
    '삼풍': ['삼풍아파트'], '신반포(한신2차)': ['신반포2'],
    '신반포(한신4차)': ['신반포4'], '장미(1차)': ['장미1'],
    '아시아선수촌': ['아시아선수촌아파트'], '타워팰리스(1차)': ['타워팰리스1'],
    '강동롯데캐슬퍼스트': ['롯데캐슬퍼스트'], '미성(2차)': ['미성2차'],
    '선경(1 2차)': ['선경1차', '선경2차'],
}
for phase in (5,7,9,13,14):
    ALIASES[f'목동신시가지({phase}단지)'] = [f'목동신시가지{phase}']

def name_matches(api_name, db_name, legacy):
    norm=lambda value: re.sub(r'\s+', '', value)
    if db_name in ALIASES:
        # API parentheses here contain building numbers, not phase identities.
        return norm(re.sub(r'\(.*?\)', '', api_name)) in {norm(n) for n in ALIASES[db_name]}
    return legacy(api_name, db_name)



def dong_matches(complex_row, source_dong):
    # One named complex spans two legal dongs. Do not loosen other complexes.
    if complex_row.get('name') == '래미안슈르' and complex_row.get('bjd_code', '').startswith('41290'):
        return source_dong in {'원문동', '별양동'}
    region = complex_row.get('region')
    return not region or region.split()[-1] == source_dong
