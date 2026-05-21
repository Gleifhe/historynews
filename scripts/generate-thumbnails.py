#!/usr/bin/env python3
"""
generate-thumbnails.py — Generate thumbnail versions of article images.

Creates 400px-wide thumbnails in static/images/articles/thumb/ for use
in article cards, homepage grids, and related article links.

Usage:
    python scripts/generate-thumbnails.py              # Generate all
    python scripts/generate-thumbnails.py --dry-run     # Preview only
    python scripts/generate-thumbnails.py --width 300   # Custom width
    python scripts/generate-thumbnails.py --force       # Regenerate all
"""
import argparse
from pathlib import Path
from PIL import Image

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'
thumb_dir = images_dir / 'thumb'

DEFAULT_WIDTH = 400
JPEG_QUALITY = 75


def main():
    parser = argparse.ArgumentParser(description='Generate article thumbnails')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--width', type=int, default=DEFAULT_WIDTH)
    parser.add_argument('--quality', type=int, default=JPEG_QUALITY)
    parser.add_argument('--force', action='store_true', help='Regenerate existing thumbnails')
    args = parser.parse_args()

    thumb_dir.mkdir(exist_ok=True)

    originals = sorted(images_dir.glob('*.jpg'))
    print(f'Found {len(originals)} images, generating {args.width}px thumbnails...\n')

    created = 0
    skipped = 0
    total_saved = 0

    for f in originals:
        thumb_path = thumb_dir / f.name

        if thumb_path.exists() and not args.force:
            skipped += 1
            continue

        if args.dry_run:
            created += 1
            continue

        try:
            img = Image.open(f)
            w, h = img.size

            # Resize to target width
            if w > args.width:
                ratio = args.width / w
                new_h = int(h * ratio)
                img = img.resize((args.width, new_h), Image.LANCZOS)

            # Convert to RGB if needed
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                img = bg
            elif img.mode != 'RGB':
                img = img.convert('RGB')

            img.save(thumb_path, 'JPEG', quality=args.quality, optimize=True)
            total_saved += f.stat().st_size - thumb_path.stat().st_size
            created += 1
        except Exception as e:
            print(f'  ERROR: {f.name}: {e}')

        if created % 100 == 0 and created > 0:
            print(f'  ... {created} thumbnails created')

    print(f'\n{"="*55}')
    print(f'  THUMBNAIL GENERATION')
    print(f'{"="*55}')
    print(f'  Created:   {created}')
    print(f'  Skipped:   {skipped}')
    if not args.dry_run and created > 0:
        thumb_total = sum(t.stat().st_size for t in thumb_dir.glob('*.jpg'))
        orig_total = sum(f.stat().st_size for f in originals)
        print(f'  Originals: {orig_total/1024/1024:.1f} MB ({orig_total//len(originals)//1024} KB avg)')
        print(f'  Thumbs:    {thumb_total/1024/1024:.1f} MB ({thumb_total//created//1024} KB avg)')
        print(f'  Savings:   {(orig_total-thumb_total)/1024/1024:.1f} MB per page load with thumbnails')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
