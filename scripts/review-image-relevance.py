#!/usr/bin/env python3
"""
review-image-relevance.py — Generate an image relevance review checklist.

For each article, outputs the slug, title, Wikipedia source used for the image,
and the local image path — formatted as a checklist for human review.

This cannot be fully automated because image relevance requires visual judgment
("Does this photo of a GPS satellite match an article about civilian GPS access?").

Usage:
    python scripts/review-image-relevance.py
    python scripts/review-image-relevance.py --csv image-review.csv
    python scripts/review-image-relevance.py --unreviewed   # only show unreviewed
"""
import argparse
import csv
import json
import re
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
images_dir = root / 'static' / 'images' / 'articles'
review_log = root / 'scripts' / 'image-review-log.json'

# Load slug->wiki mappings
SLUG_TO_WIKI = {}
for script_name in ['verify-image-accuracy.py', 'download-memorial-day-images.py', 'fix-all-images-final.py']:
    script_path = root / 'scripts' / script_name
    if script_path.exists():
        content = script_path.read_text(encoding='utf-8')
        for match in re.finditer(r"'([a-z0-9-]+)':\s*'([^']+)'", content):
            SLUG_TO_WIKI.setdefault(match.group(1), match.group(2))


def load_review_log():
    if review_log.exists():
        return json.loads(review_log.read_text(encoding='utf-8'))
    return {}


def main():
    parser = argparse.ArgumentParser(description='Generate image relevance review checklist')
    parser.add_argument('--csv', type=str, help='Output to CSV')
    parser.add_argument('--unreviewed', action='store_true', help='Only show unreviewed images')
    args = parser.parse_args()

    reviewed = load_review_log()
    items = []

    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue

        slug = f.stem
        img = images_dir / f'{slug}.jpg'
        if not img.exists():
            continue

        if args.unreviewed and slug in reviewed:
            continue

        content = f.read_text(encoding='utf-8')
        title_match = re.search(r'title:\s*"([^"]+)"', content)
        title = title_match.group(1) if title_match else slug

        wiki_source = SLUG_TO_WIKI.get(slug, 'unknown')
        status = 'reviewed' if slug in reviewed else 'unreviewed'
        size_kb = img.stat().st_size // 1024

        items.append({
            'slug': slug,
            'title': title,
            'wiki_source': wiki_source,
            'image_file': f'{slug}.jpg',
            'size_kb': size_kb,
            'status': status,
        })

    print(f'{"="*55}')
    print(f'  IMAGE RELEVANCE REVIEW')
    print(f'{"="*55}')
    print(f'  Total articles with images: {len(items)}')
    print(f'  Reviewed:                   {sum(1 for i in items if i["status"] == "reviewed")}')
    print(f'  Unreviewed:                 {sum(1 for i in items if i["status"] == "unreviewed")}')
    print(f'{"="*55}')

    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['slug', 'title', 'wiki_source', 'image_file', 'size_kb', 'status'])
            writer.writeheader()
            writer.writerows(items)
        print(f'\n  Saved to {args.csv}')
        print(f'  Open images in static/images/articles/ and verify each matches its article topic.')
    else:
        unreviewed = [i for i in items if i['status'] == 'unreviewed']
        if unreviewed:
            print(f'\n  UNREVIEWED ({len(unreviewed)}):')
            for item in unreviewed[:20]:
                print(f'    [ ] {item["slug"]}')
                print(f'        Title: {item["title"][:60]}')
                print(f'        Image from: {item["wiki_source"]}')
                print()
            if len(unreviewed) > 20:
                print(f'    ... and {len(unreviewed) - 20} more. Run with --csv to export all.')
        else:
            print(f'\n  [OK] All images have been reviewed')

    print(f'\n  To mark images as reviewed, add entries to:')
    print(f'  {review_log}')
    print(f'  Format: {{"slug": "approved", ...}}')


if __name__ == '__main__':
    main()
