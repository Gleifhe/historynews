#!/usr/bin/env python3
"""Fix YAML source quoting: single quotes -> double quotes for <a href> tags."""
import os
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
fixed = 0

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md'):
        continue
    content = f.read_text(encoding='utf-8')
    if "- '<a href" not in content:
        continue
    # Replace single-quoted source lines with double-quoted
    new_content = re.sub(
        r"  - '(<a href.*?</a>)'",
        r'  - "\1"',
        content
    )
    if new_content != content:
        f.write_text(new_content, encoding='utf-8')
        fixed += 1
        print(f'  Fixed: {f.name}')

print(f'\nFixed {fixed} articles')
