#!/usr/bin/env python3
"""
extract-quotes.py — Extract all quoted text from articles for manual verification.

Finds all text in quotation marks in article bodies and outputs them
with attribution context for human fact-checking.

Usage:
    python scripts/extract-quotes.py
    python scripts/extract-quotes.py --article slug
    python scripts/extract-quotes.py --csv quotes.csv
"""
import argparse
import csv
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def extract_quotes(body):
    """Extract all quoted text from article body."""
    quotes = []

    # Match "quoted text" (straight quotes)
    for m in re.finditer(r'"([^"]{10,})"', body):
        # Get surrounding context (20 chars before)
        start = max(0, m.start() - 80)
        context = body[start:m.start()].strip().split('\n')[-1].strip()
        quotes.append({
            'text': m.group(1),
            'context': context,
        })

    # Match "quoted text" (curly quotes)
    for m in re.finditer(r'\u201c([^\u201d]{10,})\u201d', body):
        start = max(0, m.start() - 80)
        context = body[start:m.start()].strip().split('\n')[-1].strip()
        quotes.append({
            'text': m.group(1),
            'context': context,
        })

    return quotes


def main():
    parser = argparse.ArgumentParser(description='Extract quotes for verification')
    parser.add_argument('--article', type=str, help='Check single article')
    parser.add_argument('--csv', type=str, help='Output to CSV file')
    args = parser.parse_args()

    all_quotes = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        quotes = extract_quotes(body)

        for q in quotes:
            all_quotes.append({
                'slug': f.stem,
                'quote': q['text'][:200],
                'context': q['context'][:100],
            })

    print(f'Found {len(all_quotes)} quotes across articles\n')

    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['slug', 'quote', 'context'])
            writer.writeheader()
            writer.writerows(all_quotes)
        print(f'Saved to {args.csv}')
    else:
        for q in all_quotes:
            print(f'  {q["slug"]}:')
            print(f'    "{q["quote"][:120]}..."')
            print(f'    Context: {q["context"][:80]}')
            print()

    print(f'\nTotal: {len(all_quotes)} quotes to verify')


if __name__ == '__main__':
    main()
