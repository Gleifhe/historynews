"""One-off: Add sys.exit(1) on failure to scripts that always exit 0."""
import re
from pathlib import Path

scripts_dir = Path(__file__).parent
fixed = 0

# Scripts that need exit(1) when problems are found, with the variable/condition to check
SCRIPTS = {
    'check-alt-text.py': {
        'find': "print(f'  [OK] All alt text is descriptive')",
        'add_before_main_end': True,
        'condition': 'issues',
    },
    'check-tone.py': {
        'find': "flagged = len([a for a in results.values() if a])",
        'condition': 'flagged',
    },
    'check-reading-level.py': {
        'find': "print(f'  [OK]",
        'condition': 'too_easy or too_hard',  # need to check variables
    },
    'detect-duplicates.py': {
        'find': "No duplicate content detected",
        'condition': 'duplicates',
    },
    'detect-anachronisms.py': {
        'find': "No anachronisms detected",
        'condition': 'total_flags',
    },
    'duplicate-summaries.py': {
        'find': "No duplicate summaries detected",
        'condition': 'pairs',
    },
    'find-orphan-articles.py': {
        'find': "ORPHAN ARTICLES",
        'condition': 'orphans',
    },
    'check-memorial-day.py': {
        'find': "ALL CHECKS PASSED",
        'condition': 'total_errors',
    },
    'audit-images.py': {
        'find': "ALL IMAGES OK",
        'condition': 'issues',
    },
}

for script_name, info in SCRIPTS.items():
    path = scripts_dir / script_name
    if not path.exists():
        continue
    content = path.read_text(encoding='utf-8')
    
    # Check if sys.exit(1) already exists
    if 'sys.exit(1)' in content:
        continue
    
    # Ensure sys is imported
    if 'import sys' not in content:
        content = content.replace('import re', 'import re\nimport sys', 1)
        if 'import re' not in content:
            content = content.replace('import argparse', 'import argparse\nimport sys', 1)
            if 'import argparse' not in content:
                # Add at top after docstring
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import') or line.startswith('from'):
                        lines.insert(i, 'import sys')
                        break
                content = '\n'.join(lines)
    
    path.write_text(content, encoding='utf-8')
    print(f'  Ensured sys import: {script_name}')
    fixed += 1

print(f'\nProcessed {fixed} files for sys import')
print('Note: exit(1) calls must be added manually based on each script\'s logic')
