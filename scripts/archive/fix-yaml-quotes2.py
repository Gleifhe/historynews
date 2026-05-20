#!/usr/bin/env python3
"""Fix YAML source quoting: escape inner double quotes in source href attributes."""
import os
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
fixed = 0

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md'):
        continue
    content = f.read_text(encoding='utf-8')
    
    # Find source lines with nested double quotes: - "<a href="url">text</a>"
    # Fix by using single outer quotes: - '<a href="url">text</a>'
    new_content = re.sub(
        r'''  - "(<a href="[^"]*"[^"]*</a>)"''',
        r"  - '\1'",
        content
    )
    
    if new_content != content:
        f.write_text(new_content, encoding='utf-8')
        fixed += 1

print(f'Fixed {fixed} articles')
