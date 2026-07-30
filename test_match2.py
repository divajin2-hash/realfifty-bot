def clean_name(n): return n.replace("(", "").replace(")", "").replace(" ", "").strip()
print(clean_name("현대") == clean_name("현대(1~5차)"))
