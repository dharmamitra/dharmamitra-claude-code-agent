---
description: Resolve a human description (title / author / topic) to a DharmaNexus corpus filename, offline, via the local fuzzy matcher. The filename then feeds intertextuality and search queries.
argument-hint: <title / author / description, optionally with a language>
---

Query: $ARGUMENTS

Run the local text identifier and report the best candidates:

```bash
./scripts/identify-text.py "$ARGUMENTS" --top 8 --table
```

- It reads the cached corpus map (`data/corpus-index.json`) — no network call. Diacritics-insensitive
  (`yasomitra` matches `Yaśomitra`).
- If the user named a language, add `--lang sa|bo|zh|pa` to narrow it.
- If the index is missing or the matcher reports it's stale, note that `./scripts/setup.sh --force`
  rebuilds it.

Present the ranked candidates with `filename`, `displayName`, `collection` / `category`. Point out when
the top hits are a root text vs. its commentary vs. a chapter-split file, so the user picks the right one
before running `/intertextuality` or a search on it.
