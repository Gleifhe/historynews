#!/usr/bin/env python3
"""
new-article.py — Generate a new History News article scaffold.

Usage:
    python scripts/new-article.py --title "The Boston Tea Party" \
        --era "18th Century" --historydate "December 16, 1773" \
        --source "Library of Congress" --slug boston-tea-party \
        --image "https://upload.wikimedia.org/wikipedia/commons/..."

This creates a ready-to-edit markdown file in content/articles/ with
all front matter fields pre-populated. If --image is provided with a URL,
the image is automatically downloaded to static/images/articles/ and
the article references the local copy.
"""

import argparse
import datetime
import os
import re
import textwrap

TEMPLATE = textwrap.dedent("""\
---
title: "{title}"
headline: "{headline}"
summary: "{summary}"
date: {date}
historydate: "{historydate}"
era: "{era}"
source: "{source}"
image: "{image}"
imagealt: ""
imagecaption: ""
imagecredit: ""
video: ""
weight: {weight}
sources:
  - '<a href="">Primary Source</a>'
  - '<a href="">Additional Source 1</a>'
  - '<a href="">Additional Source 2</a>'
  - '<a href="">Additional Source 3</a>'
---

## [Opening Section — Grab the Reader]

[Write your opening paragraph here — set the scene, hook the reader with a dramatic moment.]

## [The Background]

[Provide context — what led up to this event?]

## [The Main Event]

[Describe what happened in detail.]

## [The Aftermath]

[What were the consequences?]

## [Why It Matters]

[Why should readers care today?]

## What We Can Learn (Personal Growth)

[2-3 paragraphs connecting the story to personal growth themes.]

## How This Connects to 2026

[2-3 paragraphs drawing parallels to current issues.]
""")


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def get_next_weight(content_dir):
    """Find the highest weight in existing articles and return +1."""
    max_weight = 0
    for f in os.listdir(content_dir):
        if not f.endswith('.md') or f == '_index.md':
            continue
        path = os.path.join(content_dir, f)
        with open(path, 'r', encoding='utf-8') as fh:
            for line in fh:
                m = re.match(r'^weight:\s*(\d+)', line)
                if m:
                    max_weight = max(max_weight, int(m.group(1)))
                    break
    return max_weight + 1


def main():
    parser = argparse.ArgumentParser(description='Create a new History News article scaffold')
    parser.add_argument('--title', required=True, help='Article title')
    parser.add_argument('--headline', default='', help='Newspaper-style headline (auto-generated if blank)')
    parser.add_argument('--summary', default='[Write a 1-2 sentence summary]', help='Article summary')
    parser.add_argument('--era', required=True, help='Historical era (e.g., "World War II", "Cold War")')
    parser.add_argument('--historydate', required=True, help='Historical date (e.g., "June 6, 1944")')
    parser.add_argument('--source', required=True, help='Primary source name')
    parser.add_argument('--slug', default='', help='URL slug (auto-generated from title if blank)')
    parser.add_argument('--image', default='', help='Image URL to download locally (Wikimedia Commons, LOC, etc.)')
    args = parser.parse_args()

    slug = args.slug if args.slug else slugify(args.title)
    headline = args.headline if args.headline else f"BREAKING: {args.title} — [Write Attention-Grabbing Headline]"

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    content_dir = os.path.join(root, 'content', 'articles')
    weight = get_next_weight(content_dir)

    # Download image locally if URL provided
    image_path = ''
    if args.image:
        image_dir = os.path.join(root, 'static', 'images', 'articles')
        os.makedirs(image_dir, exist_ok=True)
        local_file = os.path.join(image_dir, f'{slug}.jpg')
        print(f'Downloading image to static/images/articles/{slug}.jpg ...')
        try:
            import urllib.request, ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            req = urllib.request.Request(args.image, headers={
                'User-Agent': 'HistoryNews/1.0 (educational site; downloading licensed image)'
            })
            with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
                with open(local_file, 'wb') as f:
                    f.write(resp.read())
            image_path = f'/images/articles/{slug}.jpg'
            print(f'  OK — saved as {image_path}')
        except Exception as e:
            print(f'  FAILED to download image: {e}')
            print(f'  Using remote URL as fallback.')
            image_path = args.image

    output = TEMPLATE.format(
        title=args.title,
        headline=headline,
        summary=args.summary,
        date=datetime.datetime.now().isoformat()[:19],
        historydate=args.historydate,
        era=args.era,
        source=args.source,
        image=image_path,
        weight=weight
    )

    filepath = os.path.join(content_dir, f'{slug}.md')
    if os.path.exists(filepath):
        print(f'ERROR: {filepath} already exists.')
        return

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f'Created: {filepath}')
    print(f'Weight: {weight}')
    print(f'Next steps:')
    print(f'  1. Add a LOC image URL to the "image" field')
    print(f'  2. Write the article body')
    print(f'  3. Add source URLs')
    print(f'  4. Run: python scripts/validate-articles.py')


if __name__ == '__main__':
    main()
