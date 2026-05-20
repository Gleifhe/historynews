"""One-off: Create download mapping for the 8 new articles."""
import json
from pathlib import Path

root = Path(__file__).parent.parent
topics = json.loads((root / 'scripts' / 'topics-100.json').read_text(encoding='utf-8'))
images_dir = root / 'static' / 'images' / 'articles'
manifest = json.loads((root / 'scripts' / 'slug-to-wiki.json').read_text(encoding='utf-8'))

mappings = {}
for t in topics:
    slug = t['slug']
    if not (images_dir / f'{slug}.jpg').exists() and 'wiki' in t:
        mappings[slug] = t['wiki']
        if slug not in manifest:
            manifest[slug] = t['wiki']

(root / 'scripts' / 'new8-mappings.json').write_text(json.dumps(mappings, indent=2), encoding='utf-8')
manifest = dict(sorted(manifest.items()))
(root / 'scripts' / 'slug-to-wiki.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Need images for {len(mappings)} articles, manifest now {len(manifest)} entries')
