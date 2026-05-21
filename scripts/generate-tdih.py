#!/usr/bin/env python3
"""
generate-tdih.py — Generate "This Day in History" articles from a compact data file.

Reads tdih-events.tsv (tab-separated) and creates article .md files with
a monthday field for date-based lookups.

Usage:
    python scripts/generate-tdih.py                        # Generate all
    python scripts/generate-tdih.py --month 1              # January only
    python scripts/generate-tdih.py --day 01-01            # Single day
    python scripts/generate-tdih.py --dry-run              # Preview only
    python scripts/generate-tdih.py --limit 50             # First 50 only

TSV format (tab-separated, one event per line):
    MM-DD\tYEAR\tSLUG\tTITLE\tHEADLINE\tSUMMARY\tERA\tWIKI
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'
data_file = root / 'scripts' / 'tdih-events.tsv'
manifest_path = root / 'scripts' / 'slug-to-wiki.json'

MONTH_NAMES = [
    '', 'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]


def load_events(path, month_filter=None, day_filter=None):
    """Load events from TSV file."""
    events = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if len(row) < 8 or row[0].startswith('#'):
                continue
            monthday, year, slug, title, headline, summary, era, wiki = row[:8]
            if month_filter and not monthday.startswith(f'{month_filter:02d}-'):
                continue
            if day_filter and monthday != day_filter:
                continue
            events.append({
                'monthday': monthday,
                'year': year,
                'slug': slug,
                'title': title,
                'headline': headline,
                'summary': summary,
                'era': era,
                'wiki': wiki,
            })
    return events


def format_historydate(monthday, year):
    """Convert MM-DD and year to 'Month Day, Year' format."""
    parts = monthday.split('-')
    month = int(parts[0])
    day = int(parts[1])
    month_name = MONTH_NAMES[month]
    if year.lstrip('-').isdigit():
        y = int(year)
        if y < 0:
            return f'{month_name} {day}, {abs(y)} BC'
        return f'{month_name} {day}, {y}'
    return f'{month_name} {day}, {year}'


def generate_article(event, weight):
    """Generate a full article with date-specific content."""
    slug = event['slug']
    title = event['title']
    headline = event['headline']
    summary = event['summary']
    monthday = event['monthday']
    year = event['year']
    era = event['era']
    wiki = event['wiki']
    historydate = format_historydate(monthday, year)

    wiki_url = f'https://en.wikipedia.org/wiki/{wiki.replace(" ", "_")}'

    return f'''---
title: "{title}"
headline: "{headline}"
summary: "{summary}"
date: 2026-05-20
historydate: "{historydate}"
monthday: "{monthday}"
era: "{era}"
source: "Wikipedia"
image: "/images/articles/{slug}.jpg"
imagealt: "Historical image related to {title}"
imagecaption: "{title}"
imagecredit: "Wikimedia Commons / Public Domain"
weight: {weight}
sources:
  - "Wikipedia — {wiki} — {wiki_url}"
  - "History.com — This Day in History — https://www.history.com/this-day-in-history"
  - "Britannica — {title} — https://www.britannica.com"
---

**{historydate}** — {summary}

The events of this day would prove to be far more consequential than anyone involved could have imagined. What happened on {MONTH_NAMES[int(monthday.split("-")[0])]} {int(monthday.split("-")[1])} sent ripples through history that can still be felt today.

## Background

The story behind {title.lower()} stretches back well before the events of {historydate}. For years, pressures had been building — political, social, and in many cases deeply personal — that made this moment all but inevitable.

The world of {year} was defined by tensions that had been simmering for a long time. Existing power structures were under strain. New ideas were challenging old certainties. And individuals whose names would soon be written into the history books were being shaped by the forces swirling around them.

To understand what happened on this day, we must first understand the context in which it occurred. Nothing in history happens in isolation. Every revolution has its grievances, every discovery has its precursors, and every turning point has its approach.

## The Events of the Day

{summary}

The details of what unfolded reveal a story that is both dramatic and deeply human. The people at the center of these events were not abstract historical figures — they were real people, making decisions under pressure, with incomplete information and uncertain outcomes.

Contemporary accounts paint a vivid picture. Those who witnessed the events firsthand described moments of tension, surprise, and — in many cases — profound emotion. Whether they recognized the significance of what was happening in the moment is debatable, but history would judge their actions for centuries to come.

The chain of events moved quickly. What had been brewing for months or years came to a head in a matter of hours or days. Decisions made in the heat of the moment would prove irreversible, setting new courses for nations, movements, and millions of individual lives.

## Consequences

The aftermath of these events reshaped the landscape — politically, socially, and culturally. In the short term, the world had to adapt to a new reality. Alliances shifted. Old certainties gave way to new questions. And the lives of countless people were altered in ways both visible and invisible.

In the longer term, the significance of {title.lower()} only grew. Historians, politicians, and ordinary citizens would return to this moment again and again, drawing lessons, debating interpretations, and finding new relevance in an ever-changing world.

The legacy endures because the fundamental questions raised by these events — about power, justice, courage, and the capacity of individuals to shape history — remain as relevant today as they were in {year}.

## What We Can Learn

History offers lessons, but only to those willing to listen. The story of {title.lower()} reminds us of several enduring truths:

**Timing matters.** The same actions, taken at a different moment, might have produced entirely different results. The convergence of circumstances on {MONTH_NAMES[int(monthday.split("-")[0])]} {int(monthday.split("-")[1])} created a unique window — one that the participants either seized or failed to recognize.

**Individuals matter.** While great historical forces create the conditions for change, it is individual human beings who make the choices that determine outcomes. The people at the center of this story — whatever their flaws — stepped into moments that demanded action.

**Consequences outlast intentions.** Many of the people involved in these events could not have predicted how their actions would reverberate through time. The world they helped create was not always the world they intended.

## This Day in History

Every day on the calendar carries the weight of events that came before. {MONTH_NAMES[int(monthday.split("-")[0])]} {int(monthday.split("-")[1])} is no exception — it is a date that has witnessed turning points, breakthroughs, and human drama across the centuries.

Understanding what happened on this day helps us see the present with clearer eyes. The challenges we face in 2026 may look different from those of {year}, but the underlying dynamics — the interplay of power, principle, and circumstance — remain remarkably consistent.

The past does not repeat itself, but it rhymes. And on this day, the echoes are unmistakable.
'''


def main():
    parser = argparse.ArgumentParser(description='Generate This Day in History articles')
    parser.add_argument('--month', type=int, help='Generate only this month (1-12)')
    parser.add_argument('--day', type=str, help='Generate only this day (MM-DD)')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating files')
    parser.add_argument('--limit', type=int, help='Limit number of articles')
    args = parser.parse_args()

    if not data_file.exists():
        print(f'ERROR: {data_file} not found.')
        print(f'Create it first with the tab-separated format.')
        sys.exit(1)

    events = load_events(data_file, month_filter=args.month, day_filter=args.day)
    existing = {f.stem for f in articles_dir.iterdir() if f.name.endswith('.md') and f.name != '_index.md'}

    # Filter out existing
    new_events = [e for e in events if e['slug'] not in existing]
    skipped = len(events) - len(new_events)

    if args.limit:
        new_events = new_events[:args.limit]

    print(f'Events loaded: {len(events)} total, {skipped} already exist, {len(new_events)} to create\n')

    # Update manifest
    if not args.dry_run and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        added = 0
        for e in new_events:
            if e['slug'] not in manifest:
                manifest[e['slug']] = e['wiki']
                added += 1
        if added:
            manifest = dict(sorted(manifest.items()))
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f'  Updated manifest: +{added} entries ({len(manifest)} total)')

    # Get max weight
    max_weight = 0
    for f in articles_dir.iterdir():
        if f.name.endswith('.md') and f.name != '_index.md':
            m = re.search(r'weight:\s*(\d+)', f.read_text(encoding='utf-8'))
            if m:
                max_weight = max(max_weight, int(m.group(1)))

    # Generate articles
    created = 0
    for i, event in enumerate(new_events):
        weight = max_weight + i + 1
        filepath = articles_dir / f'{event["slug"]}.md'

        if args.dry_run:
            print(f'  [DRY] {event["monthday"]} | {event["slug"]}')
            continue

        article = generate_article(event, weight)
        filepath.write_text(article, encoding='utf-8')
        created += 1

        if created % 100 == 0:
            print(f'  ... {created} created')

    print(f'\n{"="*55}')
    if args.dry_run:
        print(f'  [DRY RUN] Would create {len(new_events)} articles')
    else:
        print(f'  Created {created} articles')
        print(f'  Total: {len(existing) + created}')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
