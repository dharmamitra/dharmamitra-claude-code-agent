---
description: Run a full philological pass on a passage — retrieve cross-language parallels, compare witnesses, surface variant readings and possible emendations, write a critical apparatus to output/critical-editions/.
argument-hint: <path under sources/, pasted anchor text, or segmentnr>
---

Anchor: $ARGUMENTS

Drive a philology workflow.

1. If `$ARGUMENTS` is a path, read the file and identify which canon language(s) the anchor is in. If it's a `segmentnr`, do a direct lookup via the **corpus-searcher** subagent first to retrieve the anchor text. If it's pasted text, use it as-is.

2. Delegate to the **philologist** subagent. It will:
   - Retrieve parallels via `/primary/` (`semantic`, `filter_source_language: "all"`, `max_depth: 30`, `do_ranking: false`, `--trim`).
   - Triage hits: canonical text vs. commentary citation vs. parallel passage.
   - Compare each witness against the anchor; surface variant readings, possible emendations, lacunae.
   - Drill into suspect words with follow-up `regular` searches when needed (budget: ≤5 follow-ups).
   - Write the apparatus to `output/critical-editions/<work>.md`.

3. Report back: how many parallels found, how many variants surfaced, how many emendations proposed, file path written.

Caveat: any metrical argument must be marked `meter unverified` unless the assistant is confident scanning the relevant verse form.
