#!/usr/bin/env python3
"""Fix the 11 missing Memorial Day images using alternative Wikipedia titles."""
import io
import json
import os
import re
import ssl
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
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Alternative Wikipedia titles for the 11 missing images
FIXES = {
    'post-traumatic-growth': 'Kintsugi',
}

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
                retry = e.headers.get('Retry-After', str(10 * (attempt + 1)))
                wait = int(retry) if retry.isdigit() else 10
                print(f' [HTTP {e.code}, wait {wait}s]', end='', flush=True)
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
            return False, str(e)
    return False, 'Max retries'


def main():
    print(f'Fixing {len(FIXES)} missing images...\n')

    # Phase 1: batch lookup
    print('Phase 1: Wikipedia API lookup...')
    thumb_urls = get_thumbnail_urls_batch(list(FIXES.values()))

    slug_to_url = {}
    for slug, wiki_title in FIXES.items():
        url = thumb_urls.get(wiki_title)
        if not url:
            for t, u in thumb_urls.items():
                if t.lower() == wiki_title.lower():
                    url = u
                    break
        if url:
            slug_to_url[slug] = (url, wiki_title)

    found = len(slug_to_url)
    missing = [s for s in FIXES if s not in slug_to_url]
    print(f'Found: {found}/{len(FIXES)}')
    if missing:
        print(f'Still missing: {", ".join(missing)}')
    print()

    # Phase 2: download
    ok = 0
    fail = []
    for slug, (url, wiki_title) in sorted(slug_to_url.items()):
        local_path = images_dir / f'{slug}.jpg'
        print(f'  {slug}', end='', flush=True)
        success, detail = download_and_convert(url, local_path)
        time.sleep(DL_DELAY)
        if success:
            ok += 1
            print(f' — OK ({detail}) [{wiki_title}]')
        else:
            fail.append((slug, detail))
            print(f' — FAILED ({detail})')

    print(f'\n  Downloaded: {ok}, Failed: {len(fail)}, Still missing: {len(missing)}')


if __name__ == '__main__':
    main()
