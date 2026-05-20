"""One-off: Create image download mappings for new articles."""
import json
from pathlib import Path

root = Path(__file__).parent.parent
topics = json.loads(Path(root / 'scripts' / 'topics-100.json').read_text(encoding='utf-8'))
manifest = json.loads(Path(root / 'scripts' / 'slug-to-wiki.json').read_text(encoding='utf-8'))

# Update manifest
added = 0
for t in topics:
    if t['slug'] not in manifest and 'wiki' in t:
        manifest[t['slug']] = t['wiki']
        added += 1

manifest = dict(sorted(manifest.items()))
Path(root / 'scripts' / 'slug-to-wiki.json').write_text(
    json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Added {added} new mappings, total: {len(manifest)}')

# Create download mappings
images_dir = root / 'static' / 'images' / 'articles'
new_mappings = {}
for t in topics:
    slug = t['slug']
    img = images_dir / f'{slug}.jpg'
    if not img.exists() and 'wiki' in t:
        new_mappings[slug] = t['wiki']

out = root / 'scripts' / 'new-images-mappings.json'
out.write_text(json.dumps(new_mappings, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Need images for {len(new_mappings)} articles -> {out.name}')
