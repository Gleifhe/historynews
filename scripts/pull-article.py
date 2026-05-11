#!/usr/bin/env python3
"""
pull-article.py — Pull article content from a source URL and generate a draft.

Fetches a web page, extracts key facts, and creates an article scaffold
with pre-filled content suggestions. If an image URL is provided via --image,
it is downloaded locally to static/images/articles/.

Usage:
    python scripts/pull-article.py \
        --url "https://www.history.com/topics/..." \
        --title "The Boston Tea Party" \
        --era "18th Century" \
        --historydate "December 16, 1773" \
        --image "https://upload.wikimedia.org/wikipedia/commons/..."

Requirements:
    pip install requests beautifulsoup4
"""

import argparse
import datetime
import os
import re
import sys
import textwrap

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def get_next_weight(content_dir):
    max_weight = 0
    for f in os.listdir(content_dir):
        if not f.endswith('.md') or f == '_index.md':
            continue
        with open(os.path.join(content_dir, f), 'r', encoding='utf-8') as fh:
            for line in fh:
                m = re.match(r'^weight:\s*(\d+)', line)
                if m:
                    max_weight = max(max_weight, int(m.group(1)))
                    break
    return max_weight + 1


def fetch_article(url):
    """Fetch a URL and extract the main text content."""
    headers = {'User-Agent': 'HistoryNews-ArticlePuller/1.0'}
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Remove scripts, styles, nav, footer
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # Try to find main content area
    main = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|article|body'))
    if not main:
        main = soup.body or soup

    # Extract paragraphs
    paragraphs = []
    for p in main.find_all('p'):
        text = p.get_text(strip=True)
        if len(text) > 40:
            paragraphs.append(text)

    return '\n\n'.join(paragraphs[:20])


def main():
    if not HAS_DEPS:
        print('ERROR: Install dependencies first:')
        print('  pip install requests beautifulsoup4')
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Pull article content from a URL')
    parser.add_argument('--url', required=True, help='Source URL to pull from')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--era', required=True, help='Historical era')
    parser.add_argument('--historydate', required=True, help='Historical date')
    parser.add_argument('--slug', default='', help='URL slug')
    parser.add_argument('--image', default='', help='Image URL to download locally')
    args = parser.parse_args()

    slug = args.slug if args.slug else slugify(args.title)

    # Download image locally if provided
    image_path = ''
    if args.image:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_dir = os.path.join(root, 'static', 'images', 'articles')
        os.makedirs(image_dir, exist_ok=True)
        local_file = os.path.join(image_dir, f'{slug}.jpg')
        print(f'Downloading image...')
        try:
            import urllib.request as urlreq
            import ssl as sslmod
            ctx = sslmod.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = sslmod.CERT_NONE
            req = urlreq.Request(args.image, headers={
                'User-Agent': 'HistoryNews/1.0 (educational site)'
            })
            with urlreq.urlopen(req, timeout=30, context=ctx) as resp:
                with open(local_file, 'wb') as f:
                    f.write(resp.read())
            image_path = f'/images/articles/{slug}.jpg'
            print(f'  OK — {image_path}')
        except Exception as e:
            print(f'  FAILED: {e}')
            image_path = args.image  # Fallback to remote

    print(f'Fetching content from: {args.url}')
    content = fetch_article(args.url)

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(root, 'content', 'articles')
    weight = get_next_weight(content_dir)

    # Build the draft
    draft = f"""---
title: "{args.title}"
headline: "BREAKING: {args.title} — [Write Attention-Grabbing Headline]"
summary: "[Write 1-2 sentence summary]"
date: {datetime.datetime.now().isoformat()[:19]}
historydate: "{args.historydate}"
era: "{args.era}"
source: "{args.url}"
image: "{image_path}"
imagealt: ""
imagecaption: ""
imagecredit: ""
video: ""
weight: {weight}
sources:
  - '<a href="{args.url}">Primary Source</a>'
  - '<a href="">Additional Source 1</a>'
  - '<a href="">Additional Source 2</a>'
  - '<a href="">Additional Source 3</a>'
---

<!-- ============================================
     SOURCE CONTENT (for reference — rewrite in your own words)
     ============================================ -->

<!--
{textwrap.fill(content[:3000], width=78)}
-->

## [Opening Section]

[Rewrite the story in your own words at an 8th grade reading level.]

## What We Can Learn (Personal Growth)

[Connect to personal growth themes.]

## How This Connects to 2026

[Draw parallels to current issues.]
"""

    filepath = os.path.join(content_dir, f'{slug}.md')
    if os.path.exists(filepath):
        print(f'ERROR: {filepath} already exists.')
        sys.exit(1)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(draft)

    print(f'Created draft: {filepath}')
    print(f'Word count from source: ~{len(content.split())} words')
    print(f'\nNext steps:')
    print(f'  1. Review source content in HTML comments')
    print(f'  2. Rewrite in your own words')
    print(f'  3. Add image, video, and source URLs')
    print(f'  4. Run: python scripts/validate-articles.py')


if __name__ == '__main__':
    main()
