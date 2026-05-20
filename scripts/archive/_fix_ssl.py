"""One-off: Fix SSL verification in all scripts."""
import re
from pathlib import Path

scripts_dir = Path(__file__).parent
fixed = 0

for py in sorted(scripts_dir.glob('*.py')):
    if py.name.startswith('_'):
        continue
    content = py.read_text(encoding='utf-8')
    if 'CERT_NONE' not in content:
        continue

    original = content

    # Pattern 1: Global CTX with 2 lines (check_hostname + verify_mode)
    content = re.sub(
        r'CTX = ssl\.create_default_context\(\)\nCTX\.check_hostname = False\nCTX\.verify_mode = ssl\.CERT_NONE',
        'CTX = ssl.create_default_context()',
        content
    )

    # Pattern 2: Local ctx with 2 lines
    content = re.sub(
        r'ctx = ssl\.create_default_context\(\)\n\s*ctx\.check_hostname = False\n\s*ctx\.verify_mode = ssl\.CERT_NONE',
        'ctx = ssl.create_default_context()',
        content
    )

    # Pattern 3: sslmod variant (pull-article.py)
    content = re.sub(
        r'ctx = sslmod\.create_default_context\(\)\n\s*ctx\.check_hostname = False\n\s*ctx\.verify_mode = sslmod\.CERT_NONE',
        'ctx = sslmod.create_default_context()',
        content
    )

    if content != original:
        py.write_text(content, encoding='utf-8')
        print(f'  Fixed: {py.name}')
        fixed += 1

print(f'\nFixed SSL in {fixed} files')
