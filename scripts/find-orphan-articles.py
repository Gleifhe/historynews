#!/usr/bin/env python3
"""
find-orphan-articles.py — Find articles that no other article links to.

Scans all articles for cross-links (/articles/slug/) and reports articles
with zero incoming links. These are undiscoverable content.

Usage:
    python scripts/find-orphan-articles.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def main():
    # Build link map
    incoming = {}  # slug -> set of slugs that link to it
    all_slugs = set()

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        slug = f.stem
        all_slugs.add(slug)
        incoming.setdefault(slug, set())

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        links = re.findall(r'\(/articles/([^/]+)/\)', body)
        for link in links:
            incoming.setdefault(link, set()).add(slug)

    orphans = [slug for slug in sorted(all_slugs) if len(incoming.get(slug, set())) == 0]
    well_linked = [slug for slug in all_slugs if len(incoming.get(slug, set())) >= 3]

    print(f'Cross-Link Report — {len(all_slugs)} articles\n')
    print(f'  Well-linked (3+ incoming): {len(well_linked)}')
    print(f'  Some links (1-2 incoming): {len(all_slugs) - len(orphans) - len(well_linked)}')
    print(f'  Orphans (0 incoming):      {len(orphans)}')

    if orphans:
        print(f'\n🔴 ORPHAN ARTICLES (no other article links to these):')
        for slug in orphans:
            print(f'  {slug}')

    # Also show most-linked articles
    top = sorted(incoming.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print(f'\n📊 MOST-LINKED ARTICLES (top 10):')
    for slug, linkers in top:
        print(f'  {slug}: {len(linkers)} incoming links')

    # Orphans aren't errors but signal content that needs cross-linking


if __name__ == '__main__':
    main()
