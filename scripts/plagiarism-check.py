#!/usr/bin/env python3
"""
plagiarism-check.py — Check articles for text overlap with their cited sources.

For each article, extracts 5 longest sentences from the body and searches
for exact or near-exact matches in Wikipedia's extract for that topic.
Flags sentences with >80% word overlap as potential plagiarism.

Note: This checks against Wikipedia only (free API). A full plagiarism check
would require a paid service like Copyscape or Turnitin.

Usage:
    python scripts/plagiarism-check.py
    python scripts/plagiarism-check.py --article slug
    python scripts/plagiarism-check.py --threshold 0.7   # lower = more sensitive
"""
import argparse
import re
import sys
import time
from pathlib import Path
from utils import wiki_api_request, load_slug_to_wiki, ARTICLES_DIR

articles_dir = ARTICLES_DIR

SLUG_TO_WIKI = load_slug_to_wiki()


def get_wiki_extracts_batch(titles):
    results = {}
    title_list = list(set(titles))
    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'extracts',
            'exintro': '0',
            'explaintext': '1',
            'exsectionformat': 'plain',
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            for n in data['query'].get('normalized', []):
                pass
            for r in data['query'].get('redirects', []):
                pass
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'extract' in page:
                    results[page.get('title', '')] = page['extract']
        if i + 50 < len(title_list):
            time.sleep(5)
    return results


def tokenize(text):
    return set(re.findall(r'[a-z]+', text.lower()))


def sentence_overlap(sentence, reference_text):
    s_words = tokenize(sentence)
    r_words = tokenize(reference_text)
    if not s_words or len(s_words) < 5:
        return 0
    overlap = s_words & r_words
    return len(overlap) / len(s_words)


def get_longest_sentences(text, n=5):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 40]
    sentences.sort(key=len, reverse=True)
    return sentences[:n]


def main():
    parser = argparse.ArgumentParser(description='Check for text overlap with Wikipedia')
    parser.add_argument('--article', type=str, help='Check single article')
    parser.add_argument('--threshold', type=float, default=0.8, help='Overlap threshold (0-1)')
    args = parser.parse_args()

    articles = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        if f.stem in SLUG_TO_WIKI:
            articles.append(f)

    if not articles:
        print('No articles with Wikipedia mappings found.')
        return

    print(f'Checking {len(articles)} articles for text overlap with Wikipedia...\n')

    # Batch fetch Wikipedia extracts
    print('Fetching Wikipedia extracts...')
    wiki_titles = [SLUG_TO_WIKI[f.stem] for f in articles]
    extracts = get_wiki_extracts_batch(wiki_titles)
    print(f'Got {len(extracts)} extracts\n')

    flagged = []
    checked = 0

    for f in articles:
        slug = f.stem
        wiki_title = SLUG_TO_WIKI[slug]
        wiki_text = extracts.get(wiki_title, '')
        if not wiki_text:
            for t, e in extracts.items():
                if t.lower() == wiki_title.lower():
                    wiki_text = e
                    break
        if not wiki_text:
            continue

        checked += 1
        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        # Strip markdown
        body = re.sub(r'#{1,6}\s+', '', body)
        body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)

        sentences = get_longest_sentences(body, n=8)
        for sentence in sentences:
            overlap = sentence_overlap(sentence, wiki_text)
            if overlap >= args.threshold:
                flagged.append((slug, overlap, sentence[:120]))

    print(f'{"="*55}')
    print(f'  PLAGIARISM CHECK SUMMARY')
    print(f'{"="*55}')
    print(f'  Articles checked:  {checked}')
    print(f'  Sentences checked: {checked * 8}')
    print(f'  Flags raised:      {len(flagged)}')
    print(f'  Threshold:         {args.threshold:.0%}')
    print(f'{"="*55}')

    if flagged:
        print(f'\n  HIGH OVERLAP WITH WIKIPEDIA:')
        for slug, overlap, sentence in flagged:
            print(f'    {slug} ({overlap:.0%}): "{sentence}..."')
    else:
        print(f'\n  [OK] No high-overlap sentences detected')


if __name__ == '__main__':
    main()
