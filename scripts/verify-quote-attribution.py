#!/usr/bin/env python3
"""
verify-quote-attribution.py — Extract quotes and their attributed speakers
for verification.

Finds patterns like:
  - "Quote text," said Person Name
  - Person Name wrote, "Quote text"
  - As Person Name put it, "Quote text"
  - "Quote text" — Person Name

Outputs a CSV of quote + attributed speaker + article for manual verification.

Usage:
    python scripts/verify-quote-attribution.py
    python scripts/verify-quote-attribution.py --csv quotes-to-verify.csv
    python scripts/verify-quote-attribution.py --article slug
"""
import argparse
import csv
import re
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

# Patterns for quote attribution
ATTRIBUTION_PATTERNS = [
    # "Quote," said Name
    r'"([^"]{15,}?),"?\s+(?:said|wrote|declared|proclaimed|stated|noted|observed|remarked)\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
    # Name said, "Quote"
    r'([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:said|wrote|declared|proclaimed|stated|noted|observed|remarked),?\s+"([^"]{15,}?)"',
    # As Name put it, "Quote"
    r'[Aa]s\s+([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(?:put it|explained|described it),?\s+"([^"]{15,}?)"',
    # "Quote" -- Name or "Quote" - Name
    r'"([^"]{15,}?)"\s*[—\-]+\s*([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
]


def extract_attributed_quotes(body):
    """Extract quotes with their attributed speakers."""
    quotes = []
    for pattern in ATTRIBUTION_PATTERNS:
        for match in re.finditer(pattern, body):
            groups = match.groups()
            # Determine which group is the quote and which is the person
            if len(groups) == 2:
                # Check if first group looks like a name (starts with capital, short)
                if len(groups[0]) < 50 and groups[0][0].isupper() and ' ' in groups[0]:
                    person, quote = groups[0], groups[1]
                else:
                    quote, person = groups[0], groups[1]
                quotes.append({
                    'quote': quote[:200],
                    'person': person,
                    'full_match': match.group(0)[:250],
                })
    return quotes


def main():
    parser = argparse.ArgumentParser(description='Extract and verify quote attributions')
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
        quotes = extract_attributed_quotes(body)

        for q in quotes:
            all_quotes.append({
                'slug': f.stem,
                'person': q['person'],
                'quote': q['quote'],
            })

    print(f'{"="*55}')
    print(f'  QUOTE ATTRIBUTION REPORT')
    print(f'{"="*55}')
    print(f'  Total attributed quotes found: {len(all_quotes)}')
    print(f'{"="*55}')

    # Group by person
    people = {}
    for q in all_quotes:
        people.setdefault(q['person'], []).append(q)

    print(f'\n  Unique speakers: {len(people)}')
    print(f'\n  TOP QUOTED FIGURES:')
    for person, quotes in sorted(people.items(), key=lambda x: -len(x[1]))[:15]:
        print(f'    {person}: {len(quotes)} quotes')

    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['slug', 'person', 'quote'])
            writer.writeheader()
            writer.writerows(all_quotes)
        print(f'\n  Saved to {args.csv} for verification')
    else:
        print(f'\n  Run with --csv quotes.csv to export for review')


if __name__ == '__main__':
    main()
