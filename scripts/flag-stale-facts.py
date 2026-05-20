#!/usr/bin/env python3
"""
flag-stale-facts.py — Identify articles with statistics that may need updating.

Scans articles for numbers paired with temporal language ("as of", "currently",
"today", "in 2025", specific recent years) that may become outdated.

Outputs a list of articles and the specific claims that should be re-verified
on a regular basis (annually or when circumstances change).

Usage:
    python scripts/flag-stale-facts.py
    python scripts/flag-stale-facts.py --article slug
"""
import argparse
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

# Patterns that indicate a fact may become stale
STALE_PATTERNS = [
    (r'as of \d{4}', 'as of [year]'),
    (r'as of today', 'as of today'),
    (r'currently', 'currently'),
    (r'to date', 'to date'),
    (r'at the time of (?:writing|publication)', 'at time of writing'),
    (r'in 202[0-9]', 'recent year reference'),
    (r'more than [\d,]+ (?:people|soldiers|troops|casualties|deaths|victims)', 'casualty count'),
    (r'approximately [\d,]+ (?:people|soldiers|troops|casualties|deaths|victims)', 'casualty count'),
    (r'over [\d,]+ (?:people|soldiers|troops|casualties|deaths|victims)', 'casualty count'),
    (r'\d+(?:,\d+)* (?:still|remain|unaccounted)', 'ongoing count'),
    (r'the (?:latest|most recent|newest)', 'recency claim'),
    (r'(?:has|have) (?:now |since )(?:grown|reached|exceeded|surpassed)', 'growth claim'),
    (r'continues to', 'ongoing action'),
    (r'still (?:remains|standing|active|operational|open)', 'current state'),
    (r'today[,.]', 'today reference'),
]


def main():
    parser = argparse.ArgumentParser(description='Flag potentially stale facts')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    all_stale = []
    checked = 0

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        checked += 1

        article_stale = []
        for pattern, label in STALE_PATTERNS:
            matches = list(re.finditer(pattern, body, re.IGNORECASE))
            for match in matches:
                start = max(0, match.start() - 40)
                end = min(len(body), match.end() + 60)
                context = body[start:end].replace('\n', ' ').strip()
                article_stale.append({
                    'type': label,
                    'match': match.group(0),
                    'context': context,
                })

        if article_stale:
            all_stale.append((f.stem, article_stale))

    print(f'{"="*55}')
    print(f'  STALE FACT CHECK')
    print(f'{"="*55}')
    print(f'  Articles checked:      {checked}')
    print(f'  Articles with stale:   {len(all_stale)}')
    print(f'  Total stale claims:    {sum(len(s) for _, s in all_stale)}')
    print(f'{"="*55}')

    if all_stale:
        print(f'\n  ARTICLES NEEDING PERIODIC REVIEW:')
        for slug, items in all_stale:
            print(f'\n    {slug} ({len(items)} claims):')
            for item in items[:5]:
                print(f'      [{item["type"]}] "{item["match"]}"')
                print(f'        ...{item["context"][:80]}...')
            if len(items) > 5:
                print(f'      ... and {len(items) - 5} more')
    else:
        print(f'\n  [OK] No potentially stale facts found')

    if all_stale:
        sys.exit(1)


if __name__ == '__main__':
    main()
