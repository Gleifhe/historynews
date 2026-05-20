#!/usr/bin/env python3
"""Fix all single-quoted YAML sources: convert to double-quoted, strip HTML."""
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
fixed = 0

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md'):
        continue
    content = f.read_text(encoding='utf-8')
    changed = False

    # Fix single-quoted sources: - 'text'  ->  - "text"
    new_content = re.sub(
        r"  - '(.*?)'$",
        lambda m: '  - "' + m.group(1).replace('"', "'") + '"',
        content,
        flags=re.MULTILINE
    )
    if new_content != content:
        content = new_content
        changed = True

    # Strip <em> and </em> tags from source lines
    new_content = re.sub(
        r'(<em>|</em>)',
        '',
        content
    )
    if new_content != content:
        content = new_content
        changed = True

    if changed:
        f.write_text(content, encoding='utf-8')
        fixed += 1

print(f'Fixed {fixed} articles')
