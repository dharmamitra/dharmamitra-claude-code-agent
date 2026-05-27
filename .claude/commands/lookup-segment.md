---
description: Fetch a single canonical passage by its DharmaMitra segmentnr (e.g. BO_K01_D0006:42b-3).
argument-hint: <segmentnr>
---

Segment: $ARGUMENTS

Call the **corpus-searcher** subagent with a direct lookup:

```bash
./scripts/primary-search.sh --trim <<JSON
{
  "search_input": "$ARGUMENTS",
  "source_filters": { "segmentnr": "$ARGUMENTS" }
}
JSON
```

Return the hit's title, text, summary, and `src_link` verbatim. Note: this returns the matched segment only, not adjacent context. If the user wants surrounding passages, point them at the `src_link` — the reading room has navigation.
