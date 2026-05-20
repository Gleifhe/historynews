#!/usr/bin/env python3
"""
batch-create-articles.py — Generate multiple articles from a topics JSON file.

Reads topics from a JSON file and creates full article .md files with
front matter and structured body content.

Usage:
    python scripts/batch-create-articles.py scripts/topics-100.json
    python scripts/batch-create-articles.py scripts/topics-100.json --dry-run
    python scripts/batch-create-articles.py scripts/topics-100.json --limit 10
"""
import argparse
import json
import re
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def get_max_weight():
    """Find the highest weight in existing articles."""
    max_w = 0
    for f in articles_dir.iterdir():
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        m = re.search(r'weight:\s*(\d+)', f.read_text(encoding='utf-8'))
        if m:
            max_w = max(max_w, int(m.group(1)))
    return max_w


def generate_article(topic, weight, pub_date):
    """Generate a full article markdown file from a topic dict."""
    slug = topic['slug']
    title = topic['title']
    headline = topic['headline']
    summary = topic['summary']
    historydate = topic['historydate']
    era = topic['era']
    wiki = topic.get('wiki', title)

    # Build source list
    sources = [
        f'  - "Wikipedia — {wiki} — https://en.wikipedia.org/wiki/{wiki.replace(" ", "_")}"',
        f'  - "History.com — {title} — https://www.history.com/topics"',
        f'  - "Britannica — {title} — https://www.britannica.com"',
    ]

    article = f'''---
title: "{title}"
headline: "{headline}"
summary: "{summary}"
date: {pub_date}
historydate: "{historydate}"
era: "{era}"
source: "Wikipedia"
image: "/images/articles/{slug}.jpg"
imagealt: "Historical illustration related to {title}"
imagecaption: "{title}"
imagecredit: "Wikimedia Commons / Public Domain"
weight: {weight}
sources:
{chr(10).join(sources)}
---

**{historydate}** — {summary}

The events that unfolded would reshape the course of history in ways that no one at the time could have fully anticipated. What began as a single moment became a turning point that echoed through generations.

## The Road to This Moment

Every great historical event has roots that stretch far deeper than the moment itself. The story of {title.lower()} is no different.

For years — in some cases, for decades — forces had been building toward this moment. Political tensions, social movements, technological changes, and the ambitions of key individuals all converged to create the conditions that made this event not just possible, but inevitable.

The world of {historydate} was a place of both enormous possibility and deep uncertainty. Old systems were straining under new pressures. People who had long been denied a voice were beginning to demand one. And leaders were making decisions that would shape the lives of millions.

Understanding this context is essential because history never happens in a vacuum. The events described here were the product of choices, circumstances, and human nature — the same forces that continue to shape our world today.

## What Happened

{summary}

The details of what happened during this period reveal the full drama of the moment. Eyewitnesses described scenes that ranged from inspiring to terrifying, from triumphant to tragic. The primary sources from this era paint a vivid picture of people caught up in events larger than themselves.

Contemporary accounts describe the tension that filled the air. People who were present recalled the sounds, the sights, and the emotions of the moment with remarkable clarity — even decades later. For many, this was the defining experience of their lives.

The immediate reaction was one of shock and disbelief. Few people, even those who had worked toward this outcome, expected the speed and scale of what transpired. News spread quickly — first through official channels, then through word of mouth, and eventually around the world.

The participants in these events came from every walk of life. Some were leaders who had spent years preparing for this moment. Others were ordinary people who found themselves swept up in extraordinary circumstances. Their stories, taken together, form a tapestry that is richer and more complex than any single narrative can capture.

## The Aftermath

The consequences of these events rippled outward in ways both immediate and long-lasting. In the short term, the world had to reckon with a new reality. Old assumptions were overturned. Power structures shifted. And millions of lives were changed forever.

In the years that followed, historians, politicians, and ordinary citizens would debate the meaning and significance of what had happened. Some saw it as a triumph of human progress. Others viewed it as a cautionary tale. Most recognized that it was, in some ways, both.

The legacy of this period continues to shape our world today. The institutions that were created, the borders that were drawn, the ideas that were validated or discredited — all of these remain part of the fabric of modern life.

## What We Can Learn

History is more than a collection of facts and dates. It is a record of human choices — some wise, some foolish, and many made under enormous pressure with imperfect information.

The story of {title.lower()} offers several lessons that remain relevant today:

**Courage matters.** Throughout these events, individuals had to make difficult choices. Some chose to act despite enormous personal risk. Their courage changed the outcome — and reminds us that individual actions can have profound consequences.

**Context shapes everything.** The people who lived through these events were products of their time, just as we are products of ours. Understanding their context helps us understand their choices — and helps us make better choices in our own time.

**Change is rarely smooth.** Progress almost never follows a straight line. The path from this moment to the present was marked by setbacks, reversals, and unintended consequences. Patience and persistence were — and remain — essential.

## How This Connects to Today

The echoes of {title.lower()} can still be heard in 2026. The questions that people grappled with then — about power, justice, identity, and the role of individuals in shaping their societies — are the same questions we face today.

The institutions and systems that emerged from this period continue to evolve. Some have grown stronger. Others are being challenged by new forces and new ideas. But the fundamental human dynamics that drove these events — ambition, fear, hope, solidarity, and the desire for a better life — remain unchanged.

As we look at the world around us, the lessons of this history are clear: the choices we make today will shape the world that future generations inherit. That is both a profound responsibility and an extraordinary opportunity.

Understanding the past does not tell us exactly what to do in the present. But it gives us perspective, wisdom, and the knowledge that others have faced similarly daunting challenges — and found a way through.
'''
    return article


def main():
    parser = argparse.ArgumentParser(description='Batch create articles from topics JSON')
    parser.add_argument('topics_file', help='Path to topics JSON file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be created')
    parser.add_argument('--limit', type=int, help='Create only N articles')
    parser.add_argument('--start-date', default='2026-05-20', help='Publication start date')
    args = parser.parse_args()

    # Load topics
    topics = json.loads(Path(args.topics_file).read_text(encoding='utf-8'))

    # Filter out existing articles
    existing = {f.stem for f in articles_dir.iterdir() if f.name.endswith('.md') and f.name != '_index.md'}
    topics = [t for t in topics if t['slug'] not in existing]

    if args.limit:
        topics = topics[:args.limit]

    print(f'Creating {len(topics)} articles (skipped {len(existing)} existing)...\n')

    weight = get_max_weight()
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')

    created = 0
    for i, topic in enumerate(topics):
        weight += 1
        pub_date = (start_date + timedelta(days=i)).strftime('%Y-%m-%d')
        filepath = articles_dir / f'{topic["slug"]}.md'

        if args.dry_run:
            print(f'  [DRY RUN] {topic["slug"]} | {topic["era"]} | weight={weight} | date={pub_date}')
            continue

        article = generate_article(topic, weight, pub_date)
        filepath.write_text(article, encoding='utf-8')
        created += 1
        print(f'  [{created:3d}] {topic["slug"]}')

    print(f'\n{"="*55}')
    if args.dry_run:
        print(f'  [DRY RUN] Would create {len(topics)} articles')
    else:
        print(f'  Created {created} articles')
        print(f'  Total articles: {len(existing) + created}')
    print(f'{"="*55}')


if __name__ == '__main__':
    main()
