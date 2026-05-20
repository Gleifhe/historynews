#!/usr/bin/env python3
"""
check-tone.py — Flag editorializing in historical sections of articles.

Scans article bodies for opinion language, subjective adjectives, and
editorial phrases that should only appear in the Personal Growth section.

Historical narrative sections should be factual and neutral.
Opinion and editorial language is acceptable ONLY in the "What This Means"
or "Personal Growth" sections.

Usage:
    python scripts/check-tone.py
    python scripts/check-tone.py --article slug
"""
import argparse
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

# Words/phrases that suggest editorial opinion
OPINION_MARKERS = [
    r'\bshould\b', r'\bmust\b', r'\bneed to\b', r'\bhave to\b',
    r'\bobviously\b', r'\bclearly\b', r'\bundeniably\b', r'\bundoubtedly\b',
    r'\bof course\b', r'\bneedless to say\b',
    r'\bincredible\b', r'\bamazing\b', r'\bshocking\b', r'\bunbelievable\b',
    r'\bterrifying\b', r'\bheartbreaking\b', r'\bbreathtaking\b',
    r'\bthe best\b', r'\bthe worst\b', r'\bthe greatest\b', r'\bthe most important\b',
    r'\bit is clear that\b', r'\bthere is no doubt\b', r'\bwithout question\b',
    r'\beveryone knows\b', r'\beveryone agrees\b', r'\bno one can deny\b',
    r'\bwe must\b', r'\bwe should\b', r'\bwe need\b',
    r'\bsadly\b', r'\btragically\b', r'\bfortunately\b', r'\bunfortunately\b',
    r'\bluckily\b', r'\bmiraculously\b',
]

# Sections where opinion is acceptable
OPINION_OK_HEADERS = [
    'what this means', 'personal growth', 'lessons for', 'what you can',
    'how this connects', 'core lesson', 'real-world examples',
    'what it means for you',
]


def split_sections(body):
    """Split article body into sections by ### headers."""
    sections = []
    current_header = 'lede'
    current_text = []

    for line in body.split('\n'):
        if line.startswith('### ') or line.startswith('## '):
            if current_text:
                sections.append((current_header, '\n'.join(current_text)))
            current_header = line.lstrip('#').strip().lower()
            current_text = []
        else:
            current_text.append(line)

    if current_text:
        sections.append((current_header, '\n'.join(current_text)))

    return sections


def is_opinion_ok_section(header):
    return any(ok in header for ok in OPINION_OK_HEADERS)


def check_tone(body):
    """Check for editorial language outside opinion-acceptable sections."""
    issues = []
    sections = split_sections(body)

    for header, text in sections:
        if is_opinion_ok_section(header):
            continue  # Opinion OK in growth/lessons sections

        for pattern in OPINION_MARKERS:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            for match in matches:
                # Get line context
                start = max(0, match.start() - 40)
                end = min(len(text), match.end() + 40)
                context = text[start:end].replace('\n', ' ').strip()
                issues.append({
                    'section': header,
                    'word': match.group(0),
                    'context': context,
                })

    return issues


def main():
    parser = argparse.ArgumentParser(description='Check article tone for editorializing')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    total_issues = 0
    articles_flagged = 0
    articles_clean = 0

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        issues = check_tone(body)

        if issues:
            articles_flagged += 1
            total_issues += len(issues)
            print(f'  {f.stem}: {len(issues)} editorial phrases in historical sections')
            for issue in issues[:3]:  # Show first 3
                print(f'    [{issue["section"]}] "{issue["word"]}" in: ...{issue["context"]}...')
            if len(issues) > 3:
                print(f'    ... and {len(issues) - 3} more')
        else:
            articles_clean += 1

    total = articles_flagged + articles_clean
    print(f'\n{"="*55}')
    print(f'  TONE CHECK SUMMARY')
    print(f'{"="*55}')
    print(f'  Articles checked:   {total}')
    print(f'  Clean:              {articles_clean}')
    print(f'  Flagged:            {articles_flagged}')
    print(f'  Total issues:       {total_issues}')
    print(f'{"="*55}')
    print(f'  Note: Opinion language is OK in Personal Growth sections.')
    print(f'  Only historical narrative sections are checked.')

    if total_issues:
        sys.exit(1)


if __name__ == '__main__':
    main()
