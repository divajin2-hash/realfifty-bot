import json

with open('pipeline/audit_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

issues = []
no_match_count = 0
for cn, ptps in report.items():
    complex_issues = []
    for pn, data in ptps.items():
        if data['status'] == 'NO_DB_MATCH':
            complex_issues.append(f"{pn}(매칭실패)")
            no_match_count += 1
        elif data['status'] not in ('OK', 'FIXED'):
            complex_issues.append(f"{pn}({data['status']})")
    
    if complex_issues:
        issues.append(f"- {cn}: {', '.join(complex_issues)}")

print(f"총 이슈/매칭실패 건수: {no_match_count}건\n")
for idx, iss in enumerate(issues):
    print(iss)
