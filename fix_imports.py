import re

with open('web/src/app/complex/page.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add Lucide imports
text = text.replace("import path from 'path'", "import path from 'path'\nimport { Activity, Search, AlertCircle, ArrowRight, TrendingUp, TrendingDown, Minus, Filter } from 'lucide-react'")

with open('web/src/app/complex/page.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
