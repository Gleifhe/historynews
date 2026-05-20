#!/usr/bin/env python3
"""Quick quality check for all Memorial Day articles."""
import re
import sys
from pathlib import Path

articles_dir = Path(__file__).parent.parent / 'content' / 'articles'
all_slugs = {f.stem for f in articles_dir.iterdir() if f.name.endswith('.md') and f.name != '_index.md'}

MEMORIAL_SLUGS = [
    'birth-of-decoration-day', 'general-logans-order', 'arlington-national-cemetery',
    'tomb-of-unknown-soldier', 'taps-bugle-call', 'gold-star-mothers',
    'national-moment-of-remembrance', 'culper-spy-ring', 'nathan-hale-last-words',
    'marquis-de-lafayette', '54th-massachusetts-regiment', 'clara-barton-angel-of-battlefield',
    'andersonville-prison', 'sullivan-ballou-letter', 'harlem-hellfighters',
    'sergeant-alvin-york', 'belleau-wood', 'lost-battalion-argonne', 'in-flanders-fields',
    'tuskegee-airmen', 'four-chaplains', 'navajo-code-talkers', 'audie-murphy-most-decorated',
    'sullivan-brothers', 'battle-of-midway', 'doolittle-raid', 'omaha-beach-first-wave',
    'battle-of-the-bulge', 'merchant-marines-wwii', 'rosie-the-riveter',
    'chosin-reservoir', 'forgotten-war-forgotten-heroes', 'vietnam-veterans-memorial-wall',
    'hanoi-hilton-pows', 'hamburger-hill', 'vietnam-mia-search', 'beirut-barracks-bombing',
    'pat-tillman-chose-service', 'mogadishu-black-hawk-down', 'pentagon-on-911',
    'fallujah-bloodiest-battle', 'afghanistan-war-fallen', 'navy-seal-michael-murphy',
    'pow-mia-flag', 'operation-homecoming-1973', 'dover-test', 'normandy-american-cemetery',
    'poppy-symbol-of-remembrance', 'letters-home-last-words', 'buglers-of-arlington',
    'eisenhowers-two-letters', 'buddy-system-never-alone', 'mission-first-people-always',
    'calm-is-contagious', 'after-action-review', 'the-40-percent-rule', 'embracing-the-suck',
    'post-traumatic-growth', 'viktor-frankl-was-right', 'power-of-the-debrief',
    'platoon-to-purpose', 'veteran-entrepreneur-boom', 'team-rubicon-continued-service',
    'gi-bill-changed-america-twice', 'service-doesnt-end-at-discharge',
    'letters-home-what-matters', 'foxhole-test', 'veterans-make-great-mentors',
    'brotherhood-beyond-uniform', 'coming-home-to-gratitude', 'make-your-bed-small-wins',
    'physical-fitness-mental-health', 'veterans-morning-routine',
    'preparation-is-a-lifestyle', 'servant-leadership',
]

REQUIRED_FIELDS = ['title', 'headline', 'summary', 'date', 'era', 'image', 'sources']

errors = []
warnings = []
stats = {'total': 0, 'missing_fields': 0, 'broken_links': 0, 'no_sources': 0, 'short': 0, 'yaml_issues': 0}

for slug in MEMORIAL_SLUGS:
    path = articles_dir / f'{slug}.md'
    if not path.exists():
        errors.append(f'{slug}: FILE MISSING')
        continue
    
    stats['total'] += 1
    content = path.read_text(encoding='utf-8')
    
    # Split front matter and body
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append(f'{slug}: NO FRONT MATTER')
        stats['yaml_issues'] += 1
        continue
    
    fm = parts[1]
    body = parts[2]
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if f'{field}:' not in fm:
            errors.append(f'{slug}: MISSING FIELD "{field}"')
            stats['missing_fields'] += 1
    
    # Check sources
    if 'sources:' not in fm:
        errors.append(f'{slug}: NO SOURCES')
        stats['no_sources'] += 1
    else:
        source_count = fm.count('  - "')
        if source_count < 3:
            warnings.append(f'{slug}: only {source_count} sources (want 3+)')
    
    # Check cross-links point to real articles
    links = re.findall(r'\(/articles/([^/]+)/\)', body)
    for link in links:
        if link not in all_slugs:
            errors.append(f'{slug}: BROKEN LINK to "{link}"')
            stats['broken_links'] += 1
    
    # Check word count
    words = len(body.split())
    if words < 600:
        warnings.append(f'{slug}: SHORT ({words} words)')
        stats['short'] += 1
    
    # Check for YAML apostrophe issues
    if "\\'" in fm:
        errors.append(f'{slug}: ESCAPED APOSTROPHE in YAML')
        stats['yaml_issues'] += 1
    
    # Check era is Memorial Day
    if '"Memorial Day"' not in fm:
        warnings.append(f'{slug}: era is not "Memorial Day"')
    
    # Check image exists
    img_path = Path(__file__).parent.parent / 'static' / 'images' / 'articles' / f'{slug}.jpg'
    if not img_path.exists():
        errors.append(f'{slug}: IMAGE FILE MISSING')

print(f'=== MEMORIAL DAY QUALITY CHECK ===')
print(f'Articles checked: {stats["total"]}/{len(MEMORIAL_SLUGS)}')
print()

if errors:
    print(f'ERRORS ({len(errors)}):')
    for e in errors:
        print(f'  ❌ {e}')
    print()

if warnings:
    print(f'WARNINGS ({len(warnings)}):')
    for w in warnings:
        print(f'  ⚠️  {w}')
    print()

if not errors and not warnings:
    print('ALL CHECKS PASSED')
else:
    print(f'Summary: {len(errors)} errors, {len(warnings)} warnings')
    if errors:
        sys.exit(1)
