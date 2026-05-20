#!/usr/bin/env python3
"""
Fix YAML sources: convert <a href="URL">Text</a> to plain 'Text — URL' format.
This avoids all YAML quoting issues with nested quotes.
"""
import os
import re
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
fixed = 0

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md'):
        continue
    content = f.read_text(encoding='utf-8')
    
    if '<a href=' not in content:
        continue
    
    # Convert any remaining <a href> tags to plain text
    # Handles: target="_blank", class="", etc.
    def fix_source(m):
        url = m.group(1)
        text = m.group(2)
        text = text.replace('"', '\\"')
        return f'  - "{text} — {url}"'
    
    new_content = re.sub(
        r"""  - ['"]<a href=["']([^"']+)["'][^>]*>(.*?)</a>['"]""",
        fix_source,
        content
    )
    
    if new_content != content:
        f.write_text(new_content, encoding='utf-8')
        fixed += 1

print(f'Fixed {fixed} articles')
