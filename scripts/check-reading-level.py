#!/usr/bin/env python3
"""
check-reading-level.py — Calculate Flesch-Kincaid reading level for each article.

Flags articles outside the target range (grade 8-10).
Articles below grade 6 may be too simplistic; above grade 12 too academic.

Usage:
    python scripts/check-reading-level.py
    python scripts/check-reading-level.py --article slug
"""
import argparse
import re
import sys
from pathlib import Path

root = Path(__file__).parent.parent
articles_dir = root / 'content' / 'articles'


def count_syllables(word):
    """Estimate syllable count for a word using improved heuristics."""
    word = word.lower().strip(".,;:!?\"'()-")
    if not word:
        return 0

    # Common exceptions
    exceptions = {
        'the': 1, 'he': 1, 'she': 1, 'we': 1, 'me': 1, 'be': 1,
        'are': 1, 'were': 1, 'here': 1, 'there': 1, 'where': 1,
        'every': 3, 'everything': 4, 'area': 3, 'idea': 3,
        'people': 2, 'business': 2, 'different': 3,
    }
    if word in exceptions:
        return exceptions[word]

    # Count vowel groups
    count = len(re.findall(r'[aeiouy]+', word))

    # Subtract silent e at end (but not -le, -ee, -ie)
    if word.endswith('e') and not word.endswith(('le', 'ee', 'ie', 'ye')) and len(word) > 2:
        count -= 1

    # Add back syllable for -le at end (e.g., "table", "bottle")
    if word.endswith('le') and len(word) > 2 and word[-3] not in 'aeiouy':
        count += 1

    # Subtract for -ed ending that isn't a syllable (e.g., "jumped" but not "created")
    if word.endswith('ed') and len(word) > 3 and word[-3] not in 'dt':
        count -= 1

    # -es ending: not a syllable unless preceded by s, x, z, ch, sh
    if word.endswith('es') and len(word) > 3:
        if not re.search(r'(s|x|z|ch|sh)es$', word):
            count -= 1

    return max(count, 1)


def flesch_kincaid_grade(text):
    """Calculate Flesch-Kincaid Grade Level."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'[a-zA-Z]+', text)

    if not sentences or not words:
        return 0

    total_sentences = len(sentences)
    total_words = len(words)
    total_syllables = sum(count_syllables(w) for w in words)

    grade = (0.39 * total_words / total_sentences) + (11.8 * total_syllables / total_words) - 15.59
    return round(grade, 1)


def flesch_reading_ease(text):
    """Calculate Flesch Reading Ease score."""
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'[a-zA-Z]+', text)

    if not sentences or not words:
        return 0

    total_sentences = len(sentences)
    total_words = len(words)
    total_syllables = sum(count_syllables(w) for w in words)

    score = 206.835 - (1.015 * total_words / total_sentences) - (84.6 * total_syllables / total_words)
    return round(score, 1)


def main():
    parser = argparse.ArgumentParser(description='Check reading levels')
    parser.add_argument('--article', type=str, help='Check single article')
    args = parser.parse_args()

    results = []
    for f in sorted(articles_dir.iterdir()):
        if not f.name.endswith('.md') or f.name == '_index.md':
            continue
        if args.article and f.stem != args.article:
            continue

        content = f.read_text(encoding='utf-8')
        body = content.split('---', 2)[2] if '---' in content else content
        # Strip markdown formatting
        body = re.sub(r'#{1,6}\s+', '', body)
        body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)
        body = re.sub(r'[*_]{1,3}', '', body)

        grade = flesch_kincaid_grade(body)
        ease = flesch_reading_ease(body)
        words = len(re.findall(r'[a-zA-Z]+', body))

        results.append({
            'slug': f.stem,
            'grade': grade,
            'ease': ease,
            'words': words,
        })

    # Sort by grade level
    results.sort(key=lambda x: x['grade'])

    too_easy = [r for r in results if r['grade'] < 6]
    target = [r for r in results if 6 <= r['grade'] <= 12]
    too_hard = [r for r in results if r['grade'] > 12]

    avg_grade = sum(r['grade'] for r in results) / len(results) if results else 0

    print(f'Reading Level Report — {len(results)} articles\n')
    print(f'  Average grade level: {avg_grade:.1f}')
    print(f'  Target range: 8-10 (8th-10th grade)')
    print(f'  In range (6-12): {len(target)}')
    print(f'  Too easy (<6):  {len(too_easy)}')
    print(f'  Too hard (>12): {len(too_hard)}')

    if too_easy:
        print(f'\n⚠️  TOO EASY (below grade 6):')
        for r in too_easy:
            print(f'  {r["slug"]}: grade {r["grade"]}, ease {r["ease"]}, {r["words"]} words')

    if too_hard:
        print(f'\n⚠️  TOO HARD (above grade 12):')
        for r in too_hard:
            print(f'  {r["slug"]}: grade {r["grade"]}, ease {r["ease"]}, {r["words"]} words')

    if not too_easy and not too_hard:
        print(f'\n✅ All articles within acceptable range')


if __name__ == '__main__':
    main()
