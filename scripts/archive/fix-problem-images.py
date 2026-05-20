#!/usr/bin/env python3
"""
fix-problem-images.py — Fix all broken/wrong-format/missing images.

Uses Wikipedia API with pithumbsize to get JPEG/PNG thumbnails from CDN
(even for SVG originals — Wikimedia renders SVGs as PNG thumbnails).
"""
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
USER_AGENT = 'HistoryNewsBot/1.0 (https://github.com/gleifhe/historynews; educational history site) python-urllib'
CTX = ssl.create_default_context()

# All problem slugs mapped to correct Wikipedia titles
FIXES = {
    'good-friday-agreement': 'Northern Ireland',
    'doctors-without-borders': 'Médecins Sans Frontières',
}

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'
articles_dir = root / 'content' / 'articles'


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


def get_thumbnail_urls(titles, width=1200):
    """Batch query Wikipedia for thumbnail URLs. Returns {title: thumb_url}."""
    results = {}
    title_list = list(titles)
    for batch_start in range(0, len(title_list), 50):
        batch = title_list[batch_start:batch_start + 50]
        data = wiki_api_request({
            'action': 'query',
            'titles': '|'.join(batch),
            'prop': 'pageimages',
            'piprop': 'thumbnail',
            'pithumbsize': str(width),
            'redirects': '1',
        })
        if data and 'query' in data and 'pages' in data['query']:
            for page_id, page in data['query']['pages'].items():
                if page_id != '-1' and 'thumbnail' in page:
                    results[page.get('title', '')] = page['thumbnail']['source']
        if batch_start + 50 < len(title_list):
            time.sleep(5)
    return results


def download_and_save(url, local_path):
    """Download image and convert to JPEG."""
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
                print(f' 429 wait {wait}s...', end=' ', flush=True)
                time.sleep(wait)
                continue
            return False, f'HTTP {e.code}'
        except Exception as e:
            return False, str(e)
    return False, 'Max retries'


def update_front_matter(filepath, new_image_path):
    content = filepath.read_text(encoding='utf-8')
    content = re.sub(r'image:\s*"[^"]*"', f'image: "{new_image_path}"', content, count=1)
    filepath.write_text(content, encoding='utf-8')


def main():
    print(f'Fixing {len(FIXES)} problem images...\n')
    
    # Step 1: Get all thumbnail URLs in one batch
    print('Querying Wikipedia API for thumbnail URLs...')
    wiki_titles = set(FIXES.values())
    thumb_urls = get_thumbnail_urls(wiki_titles)
    
    # Map back to slugs
    slug_to_url = {}
    for slug, wiki_title in FIXES.items():
        # Find matching title (case-insensitive)
        for found_title, url in thumb_urls.items():
            if found_title.lower() == wiki_title.lower() or found_title == wiki_title:
                slug_to_url[slug] = (url, found_title)
                break
    
    found = len(slug_to_url)
    missing = [s for s in FIXES if s not in slug_to_url]
    print(f'Found thumbnails: {found}/{len(FIXES)}')
    if missing:
        print(f'No thumbnail for: {", ".join(missing)}')
    print()
    
    # Step 2: Download and fix each
    fixed = 0
    failed = []
    
    for slug, (url, wiki_title) in sorted(slug_to_url.items()):
        local_path = images_dir / f'{slug}.jpg'
        hugo_path = f'/images/articles/{slug}.jpg'
        article_path = articles_dir / f'{slug}.md'
        
        # Delete existing broken file
        if local_path.exists():
            try:
                local_path.unlink()
            except PermissionError:
                # File locked — try renaming first
                temp = local_path.with_suffix('.old')
                try:
                    local_path.rename(temp)
                    temp.unlink()
                except Exception:
                    print(f' — SKIPPED (file locked)')
                    failed.append((slug, 'File locked by another process'))
                    continue
        
        print(f'  {slug}', end='', flush=True)
        success, detail = download_and_save(url, local_path)
        time.sleep(2)
        
        if success:
            fixed += 1
            print(f' — OK ({detail})')
            if article_path.exists():
                update_front_matter(article_path, hugo_path)
        else:
            failed.append((slug, detail))
            print(f' — FAILED ({detail})')
    
    print(f'\n{"="*50}')
    print(f'  Fixed: {fixed}/{len(slug_to_url)}')
    print(f'  Failed: {len(failed)}')
    print(f'{"="*50}')
    if failed:
        for s, d in failed:
            print(f'  {s}: {d}')


if __name__ == '__main__':
    main()
