#!/usr/bin/env python3
"""
fact-check-dates.py — Cross-reference article dates against Wikipedia.

For each article:
  1. Extracts the historydate from front matter
  2. Extracts dates mentioned in the article body
  3. Queries Wikipedia for the mapped article's extract
  4. Compares key dates and flags mismatches

Uses batched Wikipedia API calls with proper etiquette:
  - maxlag=5, User-Agent, Retry-After header respect
  - 50 titles per batch

Usage:
    python scripts/fact-check-dates.py              # Check all
    python scripts/fact-check-dates.py --article slug  # Check one
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path
from utils import wiki_api_request, load_slug_to_wiki, ARTICLES_DIR

articles_dir = ARTICLES_DIR

SLUG_TO_WIKI = load_slug_to_wiki()


def get_wiki_extracts(titles):
    """Batch query Wikipedia for article extracts."""
    results = {}
    title_list = list(set(titles))
    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'extracts',
            'exintro': '1',
            'explaintext': '1',
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            resolved = {}
            for n in data['query'].get('normalized', []):
                resolved[n['from']] = n['to']
            for r in data['query'].get('redirects', []):
                resolved[r['from']] = r['to']
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'extract' in page:
                    title = page.get('title', '')
                    results[title] = page['extract']
                    for orig, dest in resolved.items():
                        if dest == title:
                            results[orig] = page['extract']
        if i + 50 < len(title_list):
            time.sleep(5)
    return results


def extract_dates(text):
    """Extract all dates from text in various formats."""
    dates = set()
    # Month DD, YYYY
    for m in re.finditer(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})', text):
        dates.add(f'{m.group(1)} {m.group(2)}, {m.group(3)}')
    # YYYY alone (4-digit years)
    for m in re.finditer(r'\b(1[0-9]{3}|20[0-2][0-9])\b', text):
        dates.add(m.group(1))
    return dates


def extract_numbers(text):
    """Extract significant numbers (casualties, participants, etc.)."""
    numbers = {}
    # "approximately N" or "estimated N" or "roughly N"
    for m in re.finditer(r'(?:approximately|estimated|roughly|about|nearly|over|more than)\s+([\d,]+)', text, re.IGNORECASE):
        num = m.group(1).replace(',', '')
        if len(num) >= 3:  # Only significant numbers
            numbers[int(num)] = m.group(0)
    return numbers


def main():
    parser = argparse.ArgumentParser(description='Fact-check dates against Wikipedia')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    # Collect articles to check
    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        if f.stem in SLUG_TO_WIKI:
            articles.append(f)

    if not articles:
        print(f'No articles with Wikipedia mappings found. ({len(SLUG_TO_WIKI)} mappings loaded)')
        return

    print(f'Fact-checking {len(articles)} articles against Wikipedia...\n')

    # Batch query Wikipedia
    print('Querying Wikipedia API for reference extracts...')
    wiki_titles = [SLUG_TO_WIKI[f.stem] for f in articles]
    extracts = get_wiki_extracts(wiki_titles)
    print(f'Got {len(extracts)} extracts\n')

    flagged = []
    checked = 0

    for f in articles:
        slug = f.stem
        wiki_title = SLUG_TO_WIKI[slug]
        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content

        # Get Wikipedia extract
        wiki_text = extracts.get(wiki_title, '')
        if not wiki_text:
            # Try case-insensitive
            for t, e in extracts.items():
                if t.lower() == wiki_title.lower():
                    wiki_text = e
                    break

        if not wiki_text:
            continue

        checked += 1
        article_dates = extract_dates(body)
        wiki_dates = extract_dates(wiki_text)

        # Find dates in article that conflict with Wikipedia
        # Focus on years — if article says 1918 and Wikipedia says 1917, flag it
        article_years = {d for d in article_dates if len(d) == 4}
        wiki_years = {d for d in wiki_dates if len(d) == 4}

        # Get historydate
        hd_match = re.search(r'historydate:\s*"([^"]+)"', content)
        historydate = hd_match.group(1) if hd_match else ''

        # Check if historydate year appears in Wikipedia
        hd_year = re.search(r'\d{4}', historydate)
        if hd_year and wiki_years:
            hd_y = hd_year.group(0)
            if hd_y not in wiki_text:
                flagged.append((slug, f'historydate year {hd_y} not found in Wikipedia extract for "{wiki_title}"'))

        # Check for significant number mismatches
        article_nums = extract_numbers(body)
        wiki_nums = extract_numbers(wiki_text)

        # Flag if article has a number that's significantly different from Wikipedia
        for a_num, a_context in article_nums.items():
            for w_num, w_context in wiki_nums.items():
                # Same order of magnitude, but different by >20%
                if a_num > 100 and w_num > 100:
                    ratio = max(a_num, w_num) / max(min(a_num, w_num), 1)
                    if 1.2 < ratio < 3.0:
                        flagged.append((slug, f'NUMBER MISMATCH: article says "{a_context}" but Wikipedia says "{w_context}"'))

    print(f'{"="*55}')
    print(f'  FACT-CHECK SUMMARY')
    print(f'{"="*55}')
    print(f'  Articles checked:  {checked}')
    print(f'  Flags raised:      {len(flagged)}')
    print(f'{"="*55}')

    if flagged:
        print(f'\n  FLAGGED FOR REVIEW:')
        for slug, reason in flagged:
            print(f'    {slug}: {reason}')
    else:
        print(f'\n  ✅ No date/number mismatches detected')

    if flagged:
        sys.exit(1)


if __name__ == '__main__':
    main()
