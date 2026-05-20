#!/usr/bin/env python3
"""
duplicate-summaries.py — Detect near-duplicate article summaries.

Similar summaries hurt SEO (search engines penalize duplicate meta descriptions).
Compares all article summaries pairwise and flags pairs with >60% word overlap.

Usage:
    python scripts/duplicate-summaries.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
              'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
              'that', 'this', 'it', 'its', 'as', 'not', 'no', 'has', 'had', 'have'}


def tokenize(text):
    words = set(re.findall(r'[a-z]+', text.lower()))
    return words - STOP_WORDS


def similarity(w1, w2):
    if not w1 or not w2:
        return 0
    return len(w1 & w2) / len(w1 | w2)


def main():
    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        content = f.read_text(encoding='utf-8')
        match = re.search(r'summary:\s*"([^"]+)"', content)
        if match:
            articles.append({
                'slug': f.stem,
                'summary': match.group(1),
                'words': tokenize(match.group(1)),
            })

    duplicates = []
    for i in range(len(articles)):
        for j in range(i + 1, len(articles)):
            sim = similarity(articles[i]['words'], articles[j]['words'])
            if sim > 0.6:
                duplicates.append((articles[i]['slug'], articles[j]['slug'], sim))

    duplicates.sort(key=lambda x: -x[2])

    print(f'{"="*55}')
    print(f'  DUPLICATE SUMMARY CHECK')
    print(f'{"="*55}')
    print(f'  Articles checked:  {len(articles)}')
    print(f'  Duplicate pairs:   {len(duplicates)}')
    print(f'{"="*55}')

    if duplicates:
        print(f'\n  SIMILAR SUMMARIES:')
        for s1, s2, sim in duplicates:
            print(f'    {sim:.0%} overlap: {s1} <-> {s2}')
    else:
        print(f'\n  [OK] No duplicate summaries detected')

    if duplicates:
        sys.exit(1)


if __name__ == '__main__':
    main()
