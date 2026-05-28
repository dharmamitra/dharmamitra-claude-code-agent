---
description: Search the canonical Buddhist corpus (Kangyur / Tengyur / Taishō / Pali Nikāyas / Sanskrit critical editions) for parallels to a given passage or phrase via DharmaMitra's /primary/ endpoint.
argument-hint: <query text, segmentnr, or path to a file containing the query>
---

User's query: $ARGUMENTS

Delegate to the **corpus-searcher** subagent. It will:

1. Decide `search_type`: `semantic` (default), `regular` (exact phrase / proper name), `semantic_only` (cross-script query), or direct lookup via `source_filters.segmentnr` if the user supplied one.
2. Call `./scripts/primary-search.sh --trim` with `max_depth: 30` and `do_ranking: false`.
3. Return a numbered list of hits with title, segmentnr, lang, excerpt, summary, and the verbatim `src_link`.

If the first call returns 0 hits, broaden `filter_source_language` to `"all"` and switch to `semantic_only` before giving up.
