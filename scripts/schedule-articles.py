#!/usr/bin/env python3
"""
schedule-articles.py — Set future dates on articles for drip publishing.

Takes a list of slugs and a start date, assigns consecutive dates for
scheduled publishing. Hugo won't publish future-dated articles in production.

Usage:
    python scripts/schedule-articles.py slugs.txt --start 2026-05-19
    python scripts/schedule-articles.py slugs.txt --start 2026-05-19 --per-day 3
    python scripts/schedule-articles.py slugs.txt --start 2026-05-19 --dry-run

slugs.txt format (one slug per line):
    birth-of-decoration-day
    general-logans-order
    arlington-national-cemetery
"""
import argparse
import re
from datetime import datetime, timedelta
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def main():
    parser = argparse.ArgumentParser(description='Schedule articles for drip publishing')
    parser.add_argument('slugfile', help='Text file with one slug per line')
    parser.add_argument('--start', required=True, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--per-day', type=int, default=1, help='Articles per day')
    parser.add_argument('--dry-run', action='store_true', help='Show schedule without changing files')
    args = parser.parse_args()

    # Load slugs
    slugs = [line.strip() for line in Path(args.slugfile).read_text(encoding='utf-8').splitlines() if line.strip()]
    start_date = datetime.strptime(args.start, '%Y-%m-%d')

    print(f'Scheduling {len(slugs)} articles starting {args.start} ({args.per_day}/day)\n')

    scheduled = 0
    for i, slug in enumerate(slugs):
        day_offset = i // args.per_day
        pub_date = start_date + timedelta(days=day_offset)
        date_str = pub_date.strftime('%Y-%m-%d')

        path = articles_dir / f'{slug}.md'
        if not path.exists():
            print(f'  [SKIP] {slug} — file not found')
            continue

        print(f'  {date_str}  {slug}')

        if not args.dry_run:
            content = path.read_text(encoding='utf-8')
            content = re.sub(
                r'date:\s*\d{4}-\d{2}-\d{2}',
                f'date: {date_str}',
                content,
                count=1
            )
            path.write_text(content, encoding='utf-8')
            scheduled += 1

    print(f'\n{"="*55}')
    if args.dry_run:
        print(f'  [DRY RUN] Would schedule {len(slugs)} articles over {(len(slugs) - 1) // args.per_day + 1} days')
    else:
        print(f'  Scheduled {scheduled} articles')
    print(f'  Note: Hugo only publishes articles with dates <= today.')
    print(f'  Add a daily cron rebuild to GitHub Actions to auto-publish.')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
