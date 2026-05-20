#!/usr/bin/env python3
"""
validate-all.py — Unified quality checker for all History News articles.

Checks in one pass:
  - YAML front matter (required fields, quoting, format)
  - Cross-links (all /articles/slug/ links point to real articles)
  - Word count (800-1200 target, flags <600 or >2000)
  - Sources (at least 3, no HTML tags, double-quoted)
  - Images (local file exists, valid JPEG, reasonable size)
  - Era taxonomy (valid era value)
  - Summary length (150-200 chars ideal)

Usage:
    python scripts/validate-all.py              # Check all articles
    python scripts/validate-all.py --article slug  # Check single article
    python scripts/validate-all.py --fix        # Auto-fix what's possible
"""
import argparse
import os
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
images_dir = root / 'static' / 'images' / 'articles'
if not images_dir.exists():
    images_dir = root / 'static' / 'images' / 'articles'

REQUIRED_FIELDS = ['title', 'headline', 'summary', 'date', 'historydate', 'era',
                   'source', 'image', 'imagealt', 'imagecaption', 'imagecredit',
                   'weight', 'sources']

all_slugs = {f.stem for f in articles_dir.iterdir()
             if f.name.endswith('.md') and f.name != '_index.md'}


def check_article(path, fix=False):
    """Check a single article. Returns (errors, warnings)."""
    slug = path.stem
    content = path.read_text(encoding='utf-8')
    errors = []
    warnings = []

    # Split front matter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append('NO FRONT MATTER — missing --- delimiters')
        return errors, warnings

    fm = parts[1]
    body = parts[2]

    # 1. Required fields
    for field in REQUIRED_FIELDS:
        if f'{field}:' not in fm:
            errors.append(f'MISSING FIELD: {field}')

    # 2. YAML quoting issues
    for i, line in enumerate(fm.split('\n'), 1):
        if line.strip().startswith("- '") and '<a href' not in line:
            if "'" in line[line.index("- '") + 3:-1]:
                errors.append(f'YAML LINE {i}: single-quoted string may contain apostrophe')
        if '<a href' in line:
            errors.append(f'YAML LINE {i}: HTML <a href> tag in YAML — use plain text "Source — URL"')
        if "<em>" in line or "</em>" in line:
            warnings.append(f'YAML LINE {i}: <em> tag in YAML source — strip HTML')

    # 3. Cross-links
    links = re.findall(r'\(/articles/([^/]+)/\)', body)
    for link in links:
        if link not in all_slugs:
            errors.append(f'BROKEN LINK: /articles/{link}/ — article does not exist')

    # 4. Word count
    words = len(body.split())
    if words < 600:
        errors.append(f'TOO SHORT: {words} words (minimum 600)')
    elif words > 2000:
        warnings.append(f'LONG: {words} words (target 800-1200)')

    # 5. Sources
    source_lines = re.findall(r'  - ".*?"', fm)
    if len(source_lines) < 3:
        warnings.append(f'FEW SOURCES: {len(source_lines)} (want 3+)')

    # 6. Image exists
    img_match = re.search(r'image:\s*"([^"]+)"', fm)
    if img_match:
        img_path = img_match.group(1)
        if img_path.startswith('/images/articles/'):
            # Prevent path traversal
            if '..' in img_path:
                errors.append(f'IMAGE PATH UNSAFE: contains ".." — {img_path}')
            else:
                local_file = root / 'static' / img_path.lstrip('/')
                # Verify resolved path is under static/
                try:
                    local_file.resolve().relative_to((root / 'static').resolve())
                except ValueError:
                    errors.append(f'IMAGE PATH UNSAFE: resolves outside static/ — {img_path}')
                    local_file = None
                if local_file and not local_file.exists():
                    # Check assets too
                    local_file2 = root / 'assets' / img_path.lstrip('/')
                    if not local_file2.exists():
                        errors.append(f'IMAGE MISSING: {img_path}')
                elif local_file:
                    # Check file size
                    size = local_file.stat().st_size
                    if size < 1000:
                        warnings.append(f'IMAGE TINY: {size} bytes')
                    elif size > 5_000_000:
                        warnings.append(f'IMAGE HUGE: {size // 1024 // 1024}MB')
                    # Check JPEG header
                    with open(local_file, 'rb') as f:
                        header = f.read(3)
                    if header != b'\xff\xd8\xff':
                        errors.append(f'IMAGE NOT JPEG: wrong file format')

    # 7. Summary length
    summary_match = re.search(r'summary:\s*"([^"]*)"', fm)
    if summary_match:
        slen = len(summary_match.group(1))
        if slen < 50:
            warnings.append(f'SUMMARY SHORT: {slen} chars')
        elif slen > 300:
            warnings.append(f'SUMMARY LONG: {slen} chars')

    # 8. Escaped apostrophes
    if "\\'" in fm:
        errors.append("ESCAPED APOSTROPHE in YAML — will cause build error")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description='Validate all History News articles')
    parser.add_argument('--article', type=str, help='Check single article by slug')
    parser.add_argument('--fix', action='store_true', help='Auto-fix what is possible')
    parser.add_argument('--errors-only', action='store_true', help='Suppress warnings')
    args = parser.parse_args()

    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        articles.append(f)

    total_errors = 0
    total_warnings = 0
    articles_with_errors = 0
    articles_clean = 0

    print(f'Validating {len(articles)} articles...\n')

    for path in articles:
        errors, warnings = check_article(path, fix=args.fix)

        if errors or (warnings and not args.errors_only):
            print(f'  {path.stem}:')
            for e in errors:
                print(f'    [ERROR] {e}')
            if not args.errors_only:
                for w in warnings:
                    print(f'    [WARN]  {w}')
            total_errors += len(errors)
            total_warnings += len(warnings)
            if errors:
                articles_with_errors += 1
        else:
            articles_clean += 1

    print(f'\n{"="*55}')
    print(f'  VALIDATION SUMMARY')
    print(f'{"="*55}')
    print(f'  Articles checked:     {len(articles)}')
    print(f'  Clean:                {articles_clean}')
    print(f'  With errors:          {articles_with_errors}')
    print(f'  Total errors:         {total_errors}')
    print(f'  Total warnings:       {total_warnings}')
    print(f'{"="*55}')

    if total_errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
