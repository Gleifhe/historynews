"""One-off: Merge all SLUG_TO_WIKI dicts into slug-to-wiki.json"""
import re
import json
from pathlib import Path

scripts_dir = Path(__file__).parent
merged = {}

for script_name in [
    'verify-image-accuracy.py',
    'download-memorial-day-images.py',
    'fix-all-images-final.py',
    'fix-images-wikipedia.py',
]:
    path = scripts_dir / script_name
    if not path.exists():
        continue
    content = path.read_text(encoding='utf-8')
    for m in re.finditer(r"'([a-z0-9-]+)':\s*'([^']+)'", content):
        if m.group(1) not in merged:
            merged[m.group(1)] = m.group(2)

merged = dict(sorted(merged.items()))
out = scripts_dir / 'slug-to-wiki.json'
out.write_text(json.dumps(merged, indent=2, ensure_ascii=False), encoding='utf-8')
print(f'Wrote {len(merged)} entries to {out}')
