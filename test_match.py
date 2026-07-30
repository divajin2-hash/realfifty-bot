import re

aliases = {
    "현대(1~5차)": ["현대1", "현대2", "현대3", "현대4", "현대5", "현대(1,2차)", "현대(3차)", "현대(4차)", "현대(5차)"]
}

def clean_name(n):
    return n.replace("(", "").replace(")", "").replace(" ", "").strip()

def is_matched(api_name, db_name):
    clean_api = clean_name(api_name)
    clean_db = clean_name(db_name)
    print(f"  Comparing API: {clean_api} <-> DB: {clean_db}")
    if clean_api == clean_db: return True
    for original, alias_list in aliases.items():
        if clean_db == clean_name(original):
            for al in alias_list:
                if clean_api == clean_name(al):
                    return True
    return False

print(is_matched("현대8차", "현대(1~5차)"))
print(is_matched("현대1,2차", "현대(1~5차)"))
print(is_matched("현대", "현대(신현대)"))
print(is_matched("현대9,11,12차", "현대(신현대)"))
