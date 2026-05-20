#!/usr/bin/env python3
"""Audit all article images for issues."""
import os
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
images_dir = root / 'static' / 'images' / 'articles'

remote = []
no_image = []
local_missing = []
tiny = []
huge = []
all_local = []

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    slug = f.stem
    content = f.read_text(encoding='utf-8')
    m = re.search(r'image:\s*"([^"]+)"', content)
    if not m:
        no_image.append(slug)
        continue
    img = m.group(1)
    if img.startswith('http'):
        remote.append((slug, img[:100]))
    elif img.startswith('/images/articles/'):
        jpg = images_dir / f'{slug}.jpg'
        if not jpg.exists():
            local_missing.append(slug)
        else:
            sz = jpg.stat().st_size
            all_local.append((slug, sz))
            if sz < 5000:
                tiny.append((slug, sz))
            elif sz > 5_000_000:
                huge.append((slug, sz))

total_articles = len([f for f in articles_dir.iterdir() if f.name.endswith('.md') and f.name != '_index.md'])
total_images = len(list(images_dir.glob('*.jpg')))

print(f'Total articles: {total_articles}')
print(f'Local image files: {total_images}')
print(f'Articles with local images: {len(all_local)}')
print()

if remote:
    print(f'=== STILL REMOTE ({len(remote)}) ===')
    for s, url in remote:
        print(f'  {s}: {url}...')
    print()

if no_image:
    print(f'=== NO IMAGE FIELD ({len(no_image)}) ===')
    for s in no_image:
        print(f'  {s}')
    print()

if local_missing:
    print(f'=== LOCAL PATH BUT FILE MISSING ({len(local_missing)}) ===')
    for s in local_missing:
        print(f'  {s}')
    print()

if tiny:
    print(f'=== TINY FILES <5KB - likely broken ({len(tiny)}) ===')
    for s, sz in tiny:
        print(f'  {s}: {sz} bytes')
    print()

if huge:
    print(f'=== HUGE FILES >5MB - likely SVG/wrong format ({len(huge)}) ===')
    for s, sz in huge:
        print(f'  {s}: {sz // 1024 // 1024}MB')
    print()

# Check for non-JPEG files saved as .jpg
print(f'=== CHECKING FILE FORMATS ===')
wrong_format = []
for s, sz in all_local:
    jpg = images_dir / f'{s}.jpg'
    with open(jpg, 'rb') as fh:
        header = fh.read(16)
    # JPEG starts with FF D8 FF
    # PNG starts with 89 50 4E 47
    # SVG starts with <?xml or <svg
    if header[:3] == b'\xff\xd8\xff':
        continue  # Valid JPEG
    elif header[:4] == b'\x89PNG':
        wrong_format.append((s, 'PNG saved as .jpg', sz))
    elif header[:5] == b'<?xml' or header[:4] == b'<svg':
        wrong_format.append((s, 'SVG saved as .jpg', sz))
    elif header[:4] == b'GIF8':
        wrong_format.append((s, 'GIF saved as .jpg', sz))
    elif header[:4] == b'RIFF':
        wrong_format.append((s, 'WEBP saved as .jpg', sz))
    else:
        wrong_format.append((s, f'Unknown format: {header[:8].hex()}', sz))

if wrong_format:
    print(f'  WRONG FORMAT ({len(wrong_format)}):')
    for s, fmt, sz in wrong_format:
        print(f'    {s}: {fmt} ({sz // 1024}KB)')
else:
    print(f'  All {len(all_local)} files are valid JPEG')

if not remote and not no_image and not local_missing and not tiny and not huge and not wrong_format:
    print('\n*** ALL IMAGES OK ***')
else:
    sys.exit(1)
