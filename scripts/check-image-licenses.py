#!/usr/bin/env python3
"""
check-image-licenses.py — Re-verify Wikimedia image license status.

Queries the Wikimedia Commons API to check that each downloaded image
is still available under a free license (CC-BY-SA, public domain, etc.).

API etiquette: batched (50/call), maxlag=5, proper User-Agent.

Usage:
    python scripts/check-image-licenses.py
    python scripts/check-image-licenses.py --article slug
"""
import argparse
import argparse
import sys
import time
from pathlib import Path
from utils import wiki_api_request, load_slug_to_wiki, ARTICLES_DIR, IMAGES_DIR

articles_dir = ARTICLES_DIR
images_dir = IMAGES_DIR

SLUG_TO_WIKI = load_slug_to_wiki()

FREE_LICENSES = [
    'cc-by-sa', 'cc-by', 'public domain', 'pd', 'gfdl', 'cc0',
    'free art license', 'cc-zero', 'copyrighted free use',
]


def get_page_images_with_license(wiki_titles):
    """Get lead image filename for each Wikipedia article, then query Commons for license."""
    # Step 1: Get pageimage names
    page_images = {}
    title_list = list(set(wiki_titles))
    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'pageimages',
            'piprop': 'name',
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and page.get('pageimage'):
                    page_images[page.get('title', '')] = 'File:' + page['pageimage']
        if i + 50 < len(title_list):
            time.sleep(5)

    # Step 2: Query Commons for license metadata
    results = {}
    file_list = list(page_images.values())
    for i in range(0, len(file_list), 50):
        batch = file_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'imageinfo',
            'iiprop': 'extmetadata',
            'iiextmetadatafilter': 'LicenseShortName|UsageTerms|Restrictions',
        })
        if data and 'query' in data and 'pages' in data['query']:
            for page_id, page in data['query']['pages'].items():
                if page_id == '-1':
                    continue
                title = page.get('title', '')
                imageinfo = page.get('imageinfo', [{}])
                meta = imageinfo[0].get('extmetadata', {}) if imageinfo else {}
                license_name = meta.get('LicenseShortName', {}).get('value', 'unknown')
                usage = meta.get('UsageTerms', {}).get('value', '')
                results[title] = {
                    'license': license_name,
                    'usage_terms': usage,
                    'is_free': any(fl in license_name.lower() for fl in FREE_LICENSES),
                }
        if i + 50 < len(file_list):
            time.sleep(5)

    # Map back to wiki titles
    final = {}
    for wiki_title, file_title in page_images.items():
        if file_title in results:
            final[wiki_title] = results[file_title]
        else:
            final[wiki_title] = {'license': 'unknown', 'usage_terms': '', 'is_free': False}

    return final


def main():
    parser = argparse.ArgumentParser(description='Check image license status')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    # Find articles with local images and wiki mappings
    to_check = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue
        img = images_dir / f'{f.stem}.jpg'
        if img.exists() and f.stem in SLUG_TO_WIKI:
            to_check.append(f.stem)

    print(f'Checking image license status for {len(to_check)} articles...\n')

    # Batch check
    wiki_titles = [SLUG_TO_WIKI[slug] for slug in to_check]
    results = get_page_images_with_license(wiki_titles)

    free = 0
    non_free = []
    unknown = []

    for slug in to_check:
        wiki_title = SLUG_TO_WIKI[slug]
        if wiki_title in results:
            info = results[wiki_title]
            if info['is_free']:
                free += 1
            elif info['license'] == 'unknown':
                unknown.append((slug, wiki_title))
            else:
                non_free.append((slug, wiki_title, info['license']))
        else:
            unknown.append((slug, wiki_title))

    print(f'{"="*55}')
    print(f'  IMAGE LICENSE CHECK')
    print(f'{"="*55}')
    print(f'  Articles checked:      {len(to_check)}')
    print(f'  Free license:          {free}')
    print(f'  Non-free license:      {len(non_free)}')
    print(f'  Unknown/not found:     {len(unknown)}')
    print(f'{"="*55}')

    if non_free:
        print(f'\n  NON-FREE LICENSES (need review):')
        for slug, wiki, lic in non_free:
            print(f'    {slug} | {wiki} | {lic}')

    if unknown:
        print(f'\n  UNKNOWN/MISSING (image not found on Wikipedia):')
        for slug, wiki in unknown[:10]:
            print(f'    {slug} | {wiki}')
        if len(unknown) > 10:
            print(f'    ... and {len(unknown) - 10} more')

    if non_free:
        sys.exit(1)


if __name__ == '__main__':
    main()
