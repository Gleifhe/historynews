---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
headline: "HEADLINE: Subtitle Here"
summary: "2-3 sentence factual summary."
date: {{ .Date }}
historydate: "Month Day, Year"
era: "Era Name"
source: "Primary Source"
image: "/images/articles/{{ .File.ContentBaseName }}.jpg"
imagealt: "Descriptive alt text"
imagecaption: "Photo caption"
imagecredit: "Source of image"
weight: 200
sources:
  - "Source 1 — https://example.com"
  - "Source 2 — https://example.com"
  - "Source 3 — https://example.com"
---

Opening paragraph as breaking news from the time period. Who, what, when, where.

### Historical Context

What led to this moment. 200-300 words.

### The Event

The core narrative. 300-400 words. Use primary source quotes.

### What Happened Next

Consequences, both immediate and long-term. 200-300 words.

### What This Means for You in 2026

Connect history to personal growth. Be specific. 150-200 words.
