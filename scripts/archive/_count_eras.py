"""One-off: Count articles per era."""
import re
from pathlib import Path

eras = {}
for f in sorted(Path('content/articles').iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    m = re.search(r'era:\s*"([^"]+)"', f.read_text(encoding='utf-8'))
    if m:
        eras[m.group(1)] = eras.get(m.group(1), 0) + 1

for era, count in sorted(eras.items(), key=lambda x: -x[1]):
    print(f'  {count:3d}  {era}')
print(f'\nTotal: {sum(eras.values())} articles in {len(eras)} eras')
