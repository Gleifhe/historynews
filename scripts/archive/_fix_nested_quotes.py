# Fix nested double quotes in YAML front matter
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
fixed = 0

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    content = f.read_text(encoding='utf-8')
    parts = content.split('---', 2)
    if len(parts) < 3:
        continue

    fm = parts[1]
    new_lines = []
    changed = False

    for line in fm.split('\n'):
        # Skip source lines
        if line.strip().startswith('- '):
            new_lines.append(line)
            continue

        # Check for key: "value with "nested" quotes"
        m = re.match(r'^(\w+):\s+"(.+)"$', line)
        if m:
            key = m.group(1)
            val = m.group(2)
            # Check if val contains unescaped double quotes
            if '"' in val:
                val_fixed = val.replace('"', "'")
                line = f'{key}: "{val_fixed}"'
                changed = True
                print(f'  Fixed: {f.stem} -> {key}')

        new_lines.append(line)

    if changed:
        new_fm = '\n'.join(new_lines)
        f.write_text(f'---{new_fm}---{parts[2]}', encoding='utf-8')
        fixed += 1

print(f'\nFixed {fixed} files with nested quotes')
