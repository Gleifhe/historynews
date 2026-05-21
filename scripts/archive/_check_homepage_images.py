# Check which homepage articles have missing images
import re
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
static_dir = root / 'static'

articles = []
for f in sorted(articles_dir.iterdir()):
    if not f.name.endswith('.md') or f.name == '_index.md':
        continue
    c = f.read_text(encoding='utf-8')
    w = re.search(r'weight:\s*(\d+)', c)
    img = re.search(r"image:\s*\"([^\"]+)\"", c)
    d = re.search(r'date:\s*(\S+)', c)
    if w and img:
        weight = int(w.group(1))
        image_path = img.group(1)
        date_str = d.group(1) if d else ''
        if date_str > '2026-05-21':
            continue
        local = static_dir / image_path.lstrip('/')
        articles.append((weight, f.stem, image_path, local.exists()))

articles.sort(key=lambda x: -x[0])

missing = 0
for w, slug, img, exists in articles[:50]:
    if not exists:
        missing += 1
        print(f'  MISSING (w={w}): {slug} -> {img}')

print(f'\nTop 50 by weight: {missing} missing images')
print(f'Total articles visible (non-future): {len(articles)}')

# Also check ALL articles
all_missing = [(s, i) for _, s, i, e in articles if not e]
print(f'Total missing images across all visible articles: {len(all_missing)}')
if all_missing:
    print('First 20:')
    for s, i in all_missing[:20]:
        print(f'  {s}')
