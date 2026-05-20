#!/usr/bin/env python3
"""
detect-duplicates.py — Find articles covering the same or similar topics.

Compares article titles, headlines, and summaries using word overlap.
Flags pairs with >60% word similarity as potential duplicates.

Usage:
    python scripts/detect-duplicates.py
"""
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
              'of', 'with', 'by', 'from', 'is', 'was', 'are', 'were', 'be', 'been',
              'that', 'this', 'it', 'its', 'how', 'what', 'when', 'where', 'who',
              'which', 'why', 'not', 'no', 'as', 'if', 'than', 'then', 'so', 'up',
              'out', 'about', 'into', 'over', 'after', 'before', 'between', 'under',
              'has', 'had', 'have', 'do', 'did', 'does', 'will', 'would', 'could',
              'should', 'may', 'might', 'can', 'shall', 'must', 'more', 'most',
              'his', 'her', 'their', 'your', 'our', 'my', 'all', 'each', 'every',
              'one', 'two', 'first', 'new', 'old', 'just', 'also', 'now', 'very'}


def extract_words(text):
    """Extract significant words from text."""
    words = set(re.findall(r'[a-z]+', text.lower()))
    return words - STOP_WORDS


def similarity(words1, words2):
    """Calculate Jaccard similarity between two word sets."""
    if not words1 or not words2:
        return 0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def main():
    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        content = f.read_text(encoding='utf-8')
        title = ''
        headline = ''
        summary = ''
        historydate = ''
        for line in content.split('---', 2)[1].split('\n') if '---' in content else []:
            if line.startswith('title:'):
                title = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('headline:'):
                headline = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('summary:'):
                summary = line.split(':', 1)[1].strip().strip('"')
            elif line.startswith('historydate:'):
                historydate = line.split(':', 1)[1].strip().strip('"')

        combined = f'{title} {headline} {summary}'
        words = extract_words(combined)
        articles.append({
            'slug': f.stem,
            'title': title,
            'historydate': historydate,
            'words': words,
        })

    print(f'Checking {len(articles)} articles for duplicates...\n')

    duplicates = []
    for i in range(len(articles)):
        for j in range(i + 1, len(articles)):
            sim = similarity(articles[i]['words'], articles[j]['words'])
            if sim > 0.5:
                duplicates.append((
                    articles[i]['slug'],
                    articles[j]['slug'],
                    sim,
                    articles[i]['title'],
                    articles[j]['title'],
                ))

    # Sort by similarity descending
    duplicates.sort(key=lambda x: x[2], reverse=True)

    if duplicates:
        print(f'POTENTIAL DUPLICATES ({len(duplicates)} pairs):\n')
        for slug1, slug2, sim, title1, title2 in duplicates:
            level = '🔴' if sim > 0.7 else '🟡'
            print(f'  {level} {sim:.0%} overlap:')
            print(f'     {slug1}: "{title1}"')
            print(f'     {slug2}: "{title2}"')
            print()
    else:
        print('✅ No duplicate content detected')
    if duplicates:
        sys.exit(1)

if __name__ == '__main__':
    main()
