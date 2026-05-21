"""One-off: Map existing articles by calendar month-day and list existing slugs."""
import re
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'

MONTHS = {
    'january': '01', 'february': '02', 'march': '03', 'april': '04',
    'may': '05', 'june': '06', 'july': '07', 'august': '08',
    'september': '09', 'october': '10', 'november': '11', 'december': '12',
}

date_map = {}  # "MM-DD" -> [(slug, historydate)]
slugs = set()

for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    slugs.add(f.stem)
    content = f.read_text(encoding='utf-8')
    m = re.search(r'historydate:\s*"([^"]+)"', content)
    if not m:
        continue
    hd = m.group(1).lower().strip()

    # Try to parse "Month Day, Year" format
    for month_name, month_num in MONTHS.items():
        if hd.startswith(month_name):
            day_match = re.search(r'(\d{1,2})', hd[len(month_name):])
            if day_match:
                day = int(day_match.group(1))
                key = f'{month_num}-{day:02d}'
                date_map.setdefault(key, []).append((f.stem, m.group(1)))
            break

# Print coverage
print(f'Total articles: {len(slugs)}')
print(f'Articles with parseable month-day: {sum(len(v) for v in date_map.values())}')
print(f'Unique calendar days covered: {len(date_map)}')
print()

# Show covered dates by month
for month in range(1, 13):
    days = sorted([k for k in date_map if k.startswith(f'{month:02d}-')])
    if days:
        print(f'  Month {month:02d}: {", ".join(d.split("-")[1] for d in days)} ({len(days)} days)')
    else:
        print(f'  Month {month:02d}: (none)')

print()
# Show gaps - months with fewest coverage
for month in range(1, 13):
    days = [k for k in date_map if k.startswith(f'{month:02d}-')]
    if len(days) < 3:
        print(f'  GAP: Month {month:02d} has only {len(days)} days covered')
