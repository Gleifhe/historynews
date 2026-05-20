#!/usr/bin/env python3
"""
detect-anachronisms.py — Flag terms that didn't exist during the article's era.

Checks for words and phrases that would be anachronistic in the time period
the article covers. For example, "World War I" wasn't used until WWII;
before that it was "The Great War."

Usage:
    python scripts/detect-anachronisms.py
    python scripts/detect-anachronisms.py --article slug
"""
import argparse
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

# Term -> year it entered common usage
# Articles set before this year should not use the term
ANACHRONISM_MAP = {
    'world war i': 1939,         # Called "The Great War" before WWII
    'world war 1': 1939,
    'the first world war': 1939,
    'holocaust': 1945,           # Term not widely used until after liberation
    'genocide': 1944,            # Coined by Raphael Lemkin in 1944
    'ptsd': 1980,                # DSM-III, 1980; before: "shell shock" or "combat fatigue"
    'post-traumatic stress': 1980,
    'internet': 1983,            # ARPANET transitioned to TCP/IP
    'email': 1971,               # Ray Tomlinson
    'computer': 1945,            # ENIAC; before: human calculators
    'atomic bomb': 1945,         # Trinity test
    'nuclear': 1945,
    'antibiotic': 1941,          # First clinical use of penicillin
    'dna': 1953,                 # Watson & Crick
    'satellite': 1957,           # Sputnik
    'television': 1927,          # First demo
    'radio': 1895,               # Marconi
    'airplane': 1903,            # Wright Brothers
    'automobile': 1885,          # Benz Patent-Motorwagen
    'photograph': 1826,          # Niepce
    'telegram': 1837,            # Morse
    'machine gun': 1884,         # Maxim gun
    'trench warfare': 1914,      # WWI
    'blitzkrieg': 1939,          # WWII German doctrine
    'cold war': 1947,            # Bernard Baruch speech
    'iron curtain': 1946,        # Churchill's Fulton speech
    'third world': 1952,         # Alfred Sauvy
    'superpower': 1944,          # William T.R. Fox
    'united nations': 1945,      # Founded
    'nato': 1949,                # Founded
    'civil rights movement': 1954, # Brown v Board
}


def extract_year_from_historydate(historydate):
    """Extract the earliest year from a historydate string."""
    years = re.findall(r'\b(\d{4})\b', historydate)
    if years:
        return min(int(y) for y in years)
    return None


def main():
    parser = argparse.ArgumentParser(description='Detect anachronistic terms')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    flagged = []
    checked = 0

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        fm = content.split('---', 2)[1] if '---' in content else ''
        body = content.split('---', 2)[2] if '---' in content else content

        # Get article's time period
        hd_match = re.search(r'historydate:\s*"([^"]+)"', fm)
        if not hd_match:
            continue
        article_year = extract_year_from_historydate(hd_match.group(1))
        if not article_year:
            continue

        checked += 1
        # Strip growth/lessons sections (anachronisms are expected there)
        sections = body.split('###')
        historical_body = ''
        for section in sections:
            header = section.strip().split('\n')[0].lower() if section.strip() else ''
            if not any(ok in header for ok in ['what this means', 'personal growth', 'lessons', 'what you can', 'core lesson']):
                historical_body += section

        # Check for anachronistic terms
        for term, introduced_year in ANACHRONISM_MAP.items():
            if article_year < introduced_year:
                # Search for term in historical sections
                matches = list(re.finditer(re.escape(term), historical_body, re.IGNORECASE))
                for match in matches:
                    start = max(0, match.start() - 30)
                    end = min(len(historical_body), match.end() + 30)
                    context = historical_body[start:end].replace('\n', ' ').strip()
                    flagged.append({
                        'slug': f.stem,
                        'term': term,
                        'article_year': article_year,
                        'term_year': introduced_year,
                        'context': context,
                    })

    print(f'{"="*55}')
    print(f'  ANACHRONISM CHECK')
    print(f'{"="*55}')
    print(f'  Articles checked:  {checked}')
    print(f'  Flags raised:      {len(flagged)}')
    print(f'{"="*55}')

    if flagged:
        print(f'\n  POTENTIAL ANACHRONISMS:')
        for item in flagged:
            print(f'    {item["slug"]} (set in {item["article_year"]}):')
            print(f'      "{item["term"]}" not in use until {item["term_year"]}')
            print(f'      ...{item["context"]}...')
            print()
    else:
        print(f'\n  [OK] No anachronisms detected')

    if flagged:
        sys.exit(1)


if __name__ == '__main__':
    main()
