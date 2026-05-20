"""One-off: Fix Retry-After header parsing across all scripts."""
import re
from pathlib import Path

scripts_dir = Path(__file__).parent
fixed = 0

for py in sorted(scripts_dir.glob('*.py')):
    if py.name.startswith('_'):
        continue
    content = py.read_text(encoding='utf-8')
    if 'retry.isdigit' not in content:
        continue

    original = content
    # Replace fragile isdigit pattern with try/except
    content = re.sub(
        r"retry = e\.headers\.get\('Retry-After', str\((\d+) \* \(attempt \+ 1\)\)\)\n\s*wait = int\(retry\) if retry\.isdigit\(\) else (\d+)",
        r"retry_after = e.headers.get('Retry-After', '')\n                try:\n                    wait = int(retry_after)\n                except ValueError:\n                    wait = \1 * (attempt + 1)",
        content
    )

    if content != original:
        py.write_text(content, encoding='utf-8')
        print(f'  Fixed: {py.name}')
        fixed += 1
    else:
        print(f'  SKIP: {py.name} (pattern did not match)')

print(f'\nFixed Retry-After parsing in {fixed} files')
