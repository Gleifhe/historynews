#!/usr/bin/env python3
"""
localize-images.py — Download all remote article images to local storage.

Downloads each article's image from Wikimedia Commons or LOC, saves it locally
to static/images/articles/{slug}.jpg, and updates the article's front matter
to point to the local path.

Features:
- Respects rate limits (1-second delay between downloads)
- Resizes images to max 1200px width (if Pillow is installed)
- Skips already-downloaded images
- Reports failures for manual fixing
- Updates article front matter automatically

Usage:
    python scripts/localize-images.py              # Download all
    python scripts/localize-images.py --dry-run     # Show what would be done
    python scripts/localize-images.py --article slug # Single article
    python scripts/localize-images.py --force        # Re-download existing

Requirements:
    pip install Pillow   (optional, for resizing)
"""

import argparse
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Optional: image resizing
try:
    from PIL import Image
    import io
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Config
MAX_WIDTH = 1200       # Max image width in pixels (if Pillow available)
JPEG_QUALITY = 85      # JPEG compression quality
DELAY = 1.0            # Seconds between downloads (be polite)
USER_AGENT = 'HistoryNews/1.0 (educational history site; downloading licensed images for local hosting)'

# SSL context
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_image_dir():
    """Get/create the local images directory."""
    img_dir = get_root() / 'static' / 'images' / 'articles'
    img_dir.mkdir(parents=True, exist_ok=True)
    return img_dir


def download_image(url, local_path):
    """Download an image from a URL to a local file. Returns (success, detail)."""
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30, context=CTX) as resp:
            data = resp.read()

            if HAS_PILLOW:
                # Resize if needed
                try:
                    img = Image.open(io.BytesIO(data))
                    if img.width > MAX_WIDTH:
                        ratio = MAX_WIDTH / img.width
                        new_size = (MAX_WIDTH, int(img.height * ratio))
                        img = img.resize(new_size, Image.LANCZOS)

                    # Convert to RGB if needed (for JPEG)
                    if img.mode in ('RGBA', 'P', 'LA'):
                        img = img.convert('RGB')

                    # Save as JPEG
                    img.save(str(local_path), 'JPEG', quality=JPEG_QUALITY, optimize=True)
                    size_kb = os.path.getsize(local_path) // 1024
                    return True, f'{img.width}x{img.height}, {size_kb}KB'
                except Exception as e:
                    # If Pillow fails, save raw
                    with open(local_path, 'wb') as f:
                        f.write(data)
                    size_kb = len(data) // 1024
                    return True, f'raw save (Pillow error: {e}), {size_kb}KB'
            else:
                # Save raw without resizing
                with open(local_path, 'wb') as f:
                    f.write(data)
                size_kb = len(data) // 1024
                return True, f'{size_kb}KB (no resize - install Pillow)'

    except urllib.error.HTTPError as e:
        return False, f'HTTP {e.code}'
    except Exception as e:
        return False, str(e)


def update_article_image(filepath, new_image_path):
    """Update an article's image field to point to the local path."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the image URL with local path
    content = re.sub(
        r'image: "https?://[^"]*"',
        f'image: "{new_image_path}"',
        content
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def get_extension(url):
    """Get file extension from URL."""
    url_path = url.split('?')[0].split('#')[0]
    ext = os.path.splitext(url_path)[1].lower()
    if ext in ('.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'):
        return ext
    return '.jpg'  # Default


def main():
    parser = argparse.ArgumentParser(description='Download and localize article images')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without downloading')
    parser.add_argument('--article', type=str, help='Process single article by slug')
    parser.add_argument('--force', action='store_true', help='Re-download existing images')
    parser.add_argument('--no-update', action='store_true', help='Download only, do not update article files')
    args = parser.parse_args()

    root = get_root()
    content_dir = root / 'content' / 'articles'
    image_dir = get_image_dir()

    # Collect articles
    articles = []
    for f in sorted(content_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        with open(f, 'r', encoding='utf-8') as fh:
            content = fh.read()

        match = re.search(r'image: "(https?://[^"]+)"', content)
        if not match:
            continue  # Already local or no image

        articles.append({
            'slug': f.stem,
            'filepath': f,
            'remote_url': match.group(1),
        })

    if not articles:
        if args.article:
            print(f'Article "{args.article}" not found or already has local image.')
        else:
            print('All articles already have local images.')
        return

    print(f'{"[DRY RUN] " if args.dry_run else ""}Processing {len(articles)} articles with remote images...\n')

    if not HAS_PILLOW and not args.dry_run:
        print('NOTE: Pillow not installed. Images will be saved at original size.')
        print('      Install with: pip install Pillow\n')

    downloaded = 0
    skipped = 0
    failed = []

    for article in articles:
        slug = article['slug']
        url = article['remote_url']
        ext = get_extension(url)

        # Use .jpg for all (will convert via Pillow)
        local_filename = f'{slug}.jpg'
        local_path = image_dir / local_filename
        hugo_path = f'/images/articles/{local_filename}'

        # Skip if already exists (unless --force)
        if local_path.exists() and not args.force:
            skipped += 1
            continue

        if args.dry_run:
            print(f'  [DRY] {slug}')
            print(f'        FROM: {url[:80]}...')
            print(f'        TO:   {hugo_path}')
            downloaded += 1
            continue

        # Download
        print(f'  Downloading {slug}...', end=' ', flush=True)
        success, detail = download_image(url, local_path)

        if success:
            downloaded += 1
            print(f'OK ({detail})')

            # Update article front matter
            if not args.no_update:
                update_article_image(article['filepath'], hugo_path)

        else:
            failed.append((slug, detail))
            print(f'FAILED ({detail})')

        time.sleep(DELAY)

    # Summary
    print(f'\n{"="*50}')
    print(f'  LOCALIZE IMAGES SUMMARY')
    print(f'{"="*50}')
    print(f'  Downloaded:  {downloaded}')
    print(f'  Skipped:     {skipped} (already local)')
    print(f'  Failed:      {len(failed)}')
    print(f'  Image dir:   {image_dir}')
    if HAS_PILLOW:
        print(f'  Max width:   {MAX_WIDTH}px')
        print(f'  Quality:     {JPEG_QUALITY}%')
    print(f'{"="*50}')

    if failed:
        print(f'\n  Failed downloads (fix manually):')
        for slug, detail in failed:
            print(f'    {slug}: {detail}')

    if downloaded > 0 and not args.dry_run and not args.no_update:
        print(f'\n  Article front matter updated to use /images/articles/slug.jpg')
        print(f'  Run "hugo" to verify the build.')


if __name__ == '__main__':
    main()
