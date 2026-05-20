"""One-off: Add sys.exit(1) on failure to reporting scripts."""
from pathlib import Path

scripts_dir = Path(__file__).parent

# (script, import_after_line, exit_pattern_old, exit_pattern_new)
FIXES = [
    ('check-alt-text.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print(f'\\n  [OK] All alt text is descriptive and properly sized')\n\n\nif __name__",
     "    if issues:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('check-tone.py',
     'import re\n',
     'import re\nimport sys\n',
     "    print(f'  Note: Opinion language is OK in Personal Growth sections.')\n    print(f'  Only historical narrative sections are checked.')\n\n\nif __name__",
     "    print(f'  Note: Opinion language is OK in Personal Growth sections.')\n    print(f'  Only historical narrative sections are checked.')\n\n    if total_issues:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('detect-duplicates.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print('\\u2705 No duplicate content detected')\n\n\nif __name__",
     "    if duplicates:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('detect-anachronisms.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print(f'\\n  [OK] No anachronisms detected')\n\n\nif __name__",
     "    if flagged:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('duplicate-summaries.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print(f'\\n  [OK] No duplicate summaries detected')\n\n\nif __name__",
     "    if duplicates:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('score-sources.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print(f'\\n\\u2705 All articles have acceptable source quality')\n\n\nif __name__",
     "    if weak_articles:\n        sys.exit(1)\n\n\nif __name__",
    ),
    ('flag-stale-facts.py',
     'import re\n',
     'import re\nimport sys\n',
     "    else:\n        print(f'\\n  [OK] No potentially stale facts found')\n\n\nif __name__",
     "    if all_stale:\n        sys.exit(1)\n\n\nif __name__",
    ),
]

fixed = 0
for item in FIXES:
    script_name, old_import, new_import, old_end, new_end = item
    path = scripts_dir / script_name
    if not path.exists():
        print(f'  SKIP: {script_name} not found')
        continue
    content = path.read_text(encoding='utf-8')
    if 'sys.exit(1)' in content:
        print(f'  SKIP: {script_name} already has sys.exit(1)')
        continue

    # Add sys import
    if 'import sys' not in content:
        content = content.replace(old_import, new_import, 1)

    # Add exit(1) 
    if old_end in content:
        content = content.replace(old_end, new_end, 1)
        path.write_text(content, encoding='utf-8')
        print(f'  Fixed: {script_name}')
        fixed += 1
    else:
        print(f'  WARN: {script_name} — end pattern not found, needs manual fix')

print(f'\nFixed {fixed} files')
