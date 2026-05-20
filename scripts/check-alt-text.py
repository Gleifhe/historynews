#!/usr/bin/env python3
"""
check-alt-text.py — Flag generic, short, or missing image alt text.

Good alt text: "American soldiers wade through surf on Omaha Beach, June 6, 1944"
Bad alt text:  "image", "photo", "article image", ""

Usage:
    python scripts/check-alt-text.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

GENERIC_ALT = {'image', 'photo', 'picture', 'article image', 'img', 'header image',
               'hero image', 'featured image', 'thumbnail', 'cover', 'banner'}


def main():
    issues = []
    checked = 0

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue

        content = f.read_text(encoding='utf-8')
        fm = content.split('---', 2)[1] if '---' in content else ''
        checked += 1

        # Check imagealt
        match = re.search(r'imagealt:\s*"([^"]*)"', fm)
        if not match:
            issues.append((f.stem, 'MISSING', 'no imagealt field'))
            continue

        alt = match.group(1).strip()
        if not alt:
            issues.append((f.stem, 'EMPTY', '""'))
        elif alt.lower() in GENERIC_ALT:
            issues.append((f.stem, 'GENERIC', f'"{alt}"'))
        elif len(alt) < 10:
            issues.append((f.stem, 'TOO SHORT', f'"{alt}" ({len(alt)} chars)'))
        elif len(alt) > 200:
            issues.append((f.stem, 'TOO LONG', f'{len(alt)} chars'))

    print(f'{"="*55}')
    print(f'  ALT TEXT CHECK')
    print(f'{"="*55}')
    print(f'  Articles checked:  {checked}')
    print(f'  Issues found:      {len(issues)}')
    print(f'{"="*55}')

    if issues:
        print(f'\n  ISSUES:')
        for slug, issue_type, detail in issues:
            print(f'    {slug}: [{issue_type}] {detail}')
    else:
        print(f'\n  [OK] All alt text is descriptive and properly sized')

    if issues:
        sys.exit(1)


if __name__ == '__main__':
    main()
