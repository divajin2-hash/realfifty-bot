import re

# 1. Patch ClientGrid.tsx
with open('web/src/app/ClientGrid.tsx', 'r', encoding='utf-8') as f:
    grid_text = f.read()

# Add event listener to ClientGrid
old_grid_head = '''export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
    const [searchQuery, setSearchQuery] = useState("");
    const filtered = groupedData.filter(g => g.complex.name.replace(/\\s+/g, '').includes(searchQuery.replace(/\\s+/g, '')));'''

new_grid_head = '''export default function ClientGrid({ groupedData }: { groupedData: any[] }) {
    const [searchQuery, setSearchQuery] = useState("");

    useEffect(() => {
        const handler = (e: any) => setSearchQuery(e.detail);
        window.addEventListener('kb50_search', handler);
        return () => window.removeEventListener('kb50_search', handler);
    }, []);

    const filtered = groupedData.filter(g => g.complex.name.replace(/\\s+/g, '').includes(searchQuery.replace(/\\s+/g, '')));'''

grid_text = grid_text.replace(old_grid_head, new_grid_head)

# Remove the inline search bar html
old_inline_search = r'<div style={{ display: \'flex\', justifyContent: \'flex-end\', marginBottom: \'24px\', marginTop: \'-15px\' }}>.*?</div>\s*</div>'
grid_text = re.sub(old_inline_search, '', grid_text, flags=re.DOTALL)

with open('web/src/app/ClientGrid.tsx', 'w', encoding='utf-8') as f:
    f.write(grid_text)
print("Patched ClientGrid.tsx")

# 2. Patch page.tsx
with open('web/src/app/page.tsx', 'r', encoding='utf-8') as f:
    page_text = f.read()

if "import SearchInput from './SearchInput'" not in page_text:
    page_text = page_text.replace("import ClientGrid from './ClientGrid'", "import ClientGrid from './ClientGrid'\\nimport SearchInput from './SearchInput'")

old_sidebar_bottom = r'<div style={{ marginTop: \'auto\', padding: \'24px\' }}>\s*<div style=\{\{ backgroundColor: \'#ba1a1a\''

new_sidebar_bottom = "<div style={{ marginTop: 'auto', padding: '24px' }}>\\n                    <SearchInput />\\n                    <div style={{ backgroundColor: '#ba1a1a'"

page_text = re.sub(old_sidebar_bottom, new_sidebar_bottom, page_text)

with open('web/src/app/page.tsx', 'w', encoding='utf-8') as f:
    f.write(page_text)
print("Patched page.tsx")
