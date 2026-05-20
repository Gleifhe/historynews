#!/usr/bin/env python3
"""
check-image-budget.py — Track total image directory size and warn if too large.

Reports:
  - Total image count and size
  - Average image size
  - Largest and smallest images
  - Growth since last check (if log exists)

Warns if total exceeds budget (default 100MB).

Usage:
    python scripts/check-image-budget.py
    python scripts/check-image-budget.py --budget 150  # MB
"""
import argparse
import json
from pathlib import Path

root = Path(__file__).parent.parent
images_dir = root / 'static' / 'images' / 'articles'
budget_log = root / 'scripts' / 'image-budget-log.json'


def main():
    parser = argparse.ArgumentParser(description='Check image directory size budget')
    parser.add_argument('--budget', type=int, default=100, help='Budget in MB')
    args = parser.parse_args()

    if not images_dir.exists():
        print('No images directory found.')
        return

    images = list(images_dir.glob('*.jpg'))
    if not images:
        print('No JPEG images found.')
        return

    sizes = [(f.name, f.stat().st_size) for f in images]
    total_bytes = sum(s for _, s in sizes)
    total_mb = total_bytes / (1024 * 1024)
    avg_kb = (total_bytes / len(sizes)) / 1024
    sizes.sort(key=lambda x: x[1], reverse=True)

    budget_mb = args.budget
    usage_pct = (total_mb / budget_mb) * 100

    print(f'{"="*55}')
    print(f'  IMAGE BUDGET REPORT')
    print(f'{"="*55}')
    print(f'  Total images:     {len(images)}')
    print(f'  Total size:       {total_mb:.1f} MB / {budget_mb} MB ({usage_pct:.0f}%)')
    print(f'  Average size:     {avg_kb:.0f} KB')
    print(f'  Largest:          {sizes[0][0]} ({sizes[0][1] // 1024} KB)')
    print(f'  Smallest:         {sizes[-1][0]} ({sizes[-1][1] // 1024} KB)')
    print(f'{"="*55}')

    # Budget status
    if usage_pct > 100:
        print(f'\n  [OVER BUDGET] {total_mb:.1f} MB exceeds {budget_mb} MB limit')
        print(f'  Consider: compress images, reduce max width, or increase budget')
    elif usage_pct > 80:
        print(f'\n  [WARNING] {usage_pct:.0f}% of budget used')
    else:
        print(f'\n  [OK] Within budget ({usage_pct:.0f}% used)')

    # Large file report
    large = [(name, size) for name, size in sizes if size > 500 * 1024]
    if large:
        print(f'\n  LARGE FILES (>500KB):')
        for name, size in large[:10]:
            print(f'    {name}: {size // 1024} KB')

    # Save log for tracking growth
    current = {
        'count': len(images),
        'total_mb': round(total_mb, 1),
        'avg_kb': round(avg_kb, 0),
    }

    if budget_log.exists():
        prev = json.loads(budget_log.read_text(encoding='utf-8'))
        growth = total_mb - prev.get('total_mb', 0)
        new_images = len(images) - prev.get('count', 0)
        if growth > 0:
            print(f'\n  GROWTH SINCE LAST CHECK:')
            print(f'    +{new_images} images, +{growth:.1f} MB')

    budget_log.write_text(json.dumps(current, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
