# One-off: Fix HTML <a href> tags in YAML sources.
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'

fixed = 0
for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    content = f.read_text(encoding='utf-8')
    if '<a href' not in content:
        continue

    parts = content.split('---', 2)
    if len(parts) < 3:
        continue
    fm = parts[1]
    if '<a href' not in fm:
        continue

    # Replace HTML links in source lines with plain text
    def fix_source(line):
        # Match: - "<a href=\"url\">Text</a>" or - '<a href="url">Text</a>'
        m = re.search(r'href=\\?"([^"\\]+)\\?"[^>]*>(.*?)</a>', line)
        if m:
            url = m.group(1).strip()
            text = m.group(2).strip()
            return f'  - "{text} \u2014 {url}"'
        return line

    fm_lines = fm.split('\n')
    new_lines = []
    changed = False
    for line in fm_lines:
        if '<a href' in line:
            new_line = fix_source(line)
            if new_line != line:
                changed = True
            new_lines.append(new_line)
        else:
            new_lines.append(line)

    if changed:
        new_fm = '\n'.join(new_lines)
        new_content = f'---{new_fm}---{parts[2]}'
        f.write_text(new_content, encoding='utf-8')
        fixed += 1
        print(f'  Fixed: {f.stem}')

print(f'\nFixed {fixed} articles')
