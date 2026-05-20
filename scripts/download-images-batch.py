#!/usr/bin/env python3
"""
download-images-batch.py — Generic image downloader from a JSON mapping file.

Reads slug→Wikipedia title mappings from a JSON file, downloads CDN thumbnails
via the Wikipedia API with proper etiquette, converts to JPEG.

Replaces all one-off fix-images-*.py scripts.

Usage:
    python scripts/download-images-batch.py mappings.json
    python scripts/download-images-batch.py mappings.json --force
    python scripts/download-images-batch.py mappings.json --dry-run

Mappings JSON format:
    {"slug-name": "Wikipedia Article Title", ...}

API etiquette: batched (50/call), pithumbsize CDN, maxlag=5, Retry-After, 2s delay.
"""
import argparse
import io
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

MAX_WIDTH = 1200
JPEG_QUALITY = 85
DL_DELAY = 2.0
USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'


def wiki_api_request(params):
    base_url = 'https://en.wikipedia.org/w/api.php'
    params['format'] = 'json'
    params['maxlag'] = '5'
    url = f'{base_url}?{urllib.parse.urlencode(params)}'
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15, context=CTX) as resp:
                return json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                retry_after = e.headers.get('Retry-After', '')
                try:
                    wait = int(retry_after)
                except ValueError:
                    wait = 10 * (attempt + 1)
                time.sleep(wait)
                continue
            return None
        except Exception:
            if attempt < 2:
                time.sleep(5)
                continue
            return None
    return None


def get_thumbnail_urls_batch(wiki_titles, width=1200):
    results = {}
    title_list = list(set(wiki_titles))
    for i in range(0, len(title_list), 50):
        batch = title_list[i:i + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'pageimages',
            'piprop': 'thumbnail',
            'pithumbsize': str(width),
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            resolved = {}
            for n in data['query'].get('normalized', []):
                resolved[n['from']] = n['to']
            for r in data['query'].get('redirects', []):
                resolved[r['from']] = r['to']
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'thumbnail' in page:
                    title = page.get('title', '')
                    results[title] = page['thumbnail']['source']
                    for orig, dest in resolved.items():
                        if dest == title:
                            results[orig] = page['thumbnail']['source']
        if i + 50 < len(title_list):
            time.sleep(5)
    return results


def download_and_convert(url, local_path):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
                data = resp.read()
            img = Image.open(io.BytesIO(data))
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / img.width
                img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(str(local_path), 'JPEG', quality=JPEG_QUALITY, optimize=True)
            size_kb = os.path.getsize(local_path) // 1024
            return True, f'{img.width}x{img.height}, {size_kb}KB'
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                retry = e.headers.get('Retry-After', '20')
                wait = int(retry) if retry.isdigit() else 20
                time.sleep(wait)
                continue
            return False, f'HTTP {e.code}'
        except Exception as e:
            return False, str(e)[:80]
    return False, 'Max retries'


def main():
    parser = argparse.ArgumentParser(description='Download images from Wikipedia via JSON mapping')
    parser.add_argument('mappings', help='JSON file with slug→Wikipedia title mappings')
    parser.add_argument('--force', action='store_true', help='Re-download existing images')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be downloaded')
    args = parser.parse_args()

    # Load mappings
    mappings = json.loads(Path(args.mappings).read_text(encoding='utf-8'))
    print(f'Loaded {len(mappings)} mappings from {args.mappings}')

    # Filter to only those needing download
    to_download = {}
    for slug, wiki_title in mappings.items():
        local_path = images_dir / f'{slug}.jpg'
        if not local_path.exists() or args.force:
            to_download[slug] = wiki_title

    if not to_download:
        print('All images already exist. Use --force to re-download.')
        return

    print(f'Need to download: {len(to_download)}\n')

    if args.dry_run:
        for slug, wiki_title in sorted(to_download.items()):
            print(f'  [DRY] {slug} ← "{wiki_title}"')
        return

    # Phase 1: Batch API lookup
    print('Phase 1: Wikipedia API lookup...')
    thumb_urls = get_thumbnail_urls_batch(list(to_download.values()))
    slug_to_url = {}
    for slug, wiki_title in to_download.items():
        url = thumb_urls.get(wiki_title)
        if not url:
            for t, u in thumb_urls.items():
                if t.lower() == wiki_title.lower():
                    url = u
                    break
        if url:
            slug_to_url[slug] = (url, wiki_title)

    print(f'Found: {len(slug_to_url)}/{len(to_download)}')
    missing = [s for s in to_download if s not in slug_to_url]
    if missing:
        print(f'No thumbnail: {", ".join(missing)}')
    print()

    # Phase 2: Download
    images_dir.mkdir(parents=True, exist_ok=True)
    ok = 0
    fail = []
    for slug, (url, wiki_title) in sorted(slug_to_url.items()):
        local_path = images_dir / f'{slug}.jpg'
        print(f'  {slug}', end='', flush=True)
        success, detail = download_and_convert(url, local_path)
        time.sleep(DL_DELAY)
        if success:
            ok += 1
            print(f' — OK ({detail})')
        else:
            fail.append((slug, detail))
            print(f' — FAILED ({detail})')

    print(f'\n  Downloaded: {ok}, Failed: {len(fail)}, No thumb: {len(missing)}')
    if fail or missing:
        sys.exit(1)


if __name__ == '__main__':
    main()
