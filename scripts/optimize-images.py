#!/usr/bin/env python3
"""
optimize-images.py — Resize and compress all article images for web.

Resizes images to max 800px width and compresses to quality 80 JPEG.
Keeps originals if already smaller than target.

Usage:
    python scripts/optimize-images.py              # Optimize all
    python scripts/optimize-images.py --dry-run     # Preview only
    python scripts/optimize-images.py --max-width 600  # Custom width
"""
import argparse
from pathlib import Path
from PIL import Image

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'

DEFAULT_MAX_WIDTH = 800
JPEG_QUALITY = 80


def optimize_image(path, max_width, quality, dry_run=False):
    """Resize and compress a single image. Returns (old_size, new_size) or None."""
    old_size = path.stat().st_size

    try:
        img = Image.open(path)
    except Exception:
        return None

    w, h = img.size
    needs_resize = w > max_width

    if not needs_resize and old_size < 100_000:
        return None  # Already small enough

    if needs_resize:
        ratio = max_width / w
        new_h = int(h * ratio)
        img = img.resize((max_width, new_h), Image.LANCZOS)

    # Convert to RGB if needed (handles RGBA, P, LA modes)
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    if dry_run:
        return old_size, old_size  # Can't know new size without saving

    img.save(path, 'JPEG', quality=quality, optimize=True)
    new_size = path.stat().st_size
    return old_size, new_size


def main():
    parser = argparse.ArgumentParser(description='Optimize article images')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--max-width', type=int, default=DEFAULT_MAX_WIDTH)
    parser.add_argument('--quality', type=int, default=JPEG_QUALITY)
    args = parser.parse_args()

    files = sorted(images_dir.glob('*.jpg'))
    print(f'Processing {len(files)} images (max {args.max_width}px, quality {args.quality})...\n')

    total_old = 0
    total_new = 0
    optimized = 0
    skipped = 0

    for f in files:
        result = optimize_image(f, args.max_width, args.quality, args.dry_run)
        if result is None:
            skipped += 1
            continue
        old, new = result
        total_old += old
        total_new += new
        optimized += 1

        if optimized % 100 == 0:
            print(f'  ... {optimized} optimized')

    print(f'\n{"="*55}')
    print(f'  IMAGE OPTIMIZATION')
    print(f'{"="*55}')
    print(f'  Images processed:  {optimized}')
    print(f'  Skipped (small):   {skipped}')
    if not args.dry_run and total_old > 0:
        saved = total_old - total_new
        pct = (saved / total_old) * 100
        print(f'  Before:            {total_old/1024/1024:.1f} MB')
        print(f'  After:             {total_new/1024/1024:.1f} MB')
        print(f'  Saved:             {saved/1024/1024:.1f} MB ({pct:.0f}%)')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
