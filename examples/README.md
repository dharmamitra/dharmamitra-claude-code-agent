# Examples

Ready-to-pipe JSON bodies for both DharmaMitra endpoints. Use them to verify
your install or as templates when constructing new requests.

## Try them

```bash
# Multi-source translation (Sanskrit + Tibetan sūtra opening → English)
./scripts/cat-translate.sh --file examples/cat-translate-sutra-opening.json --pretty

# Semantic search (Tibetan corpus, English query)
./scripts/primary-search.sh --file examples/primary-search-semantic.json --trim

# Lexical exact-phrase search (Sanskrit)
./scripts/primary-search.sh --file examples/primary-search-regular.json --trim

# Direct segment lookup by ID
./scripts/primary-search.sh --file examples/primary-search-by-segmentnr.json --trim

# Intertextuality: every parallel for a set of segments
./scripts/nexus.sh matches --file examples/nexus-matches.json --agg

# Intertextuality: a whole text's intersection with the rest of the corpus
./scripts/nexus.sh table --file examples/nexus-table.json --agg

# Resolve a human description to a corpus filename (local, offline)
./scripts/identify-text.py "yasomitra abhidharma commentary" --table
```

The translation call takes 3–8 seconds. Search calls take 0.3–3 seconds.
DharmaNexus `matches` / `table` calls take ~1–5 seconds; `identify-text.py` is instant
(it reads the local `data/corpus-index.json`, built once by `./scripts/setup.sh`).

## What each example demonstrates

- **`cat-translate-sutra-opening.json`** — the classic "thus have I heard" opening, given as two witnesses (Sanskrit + Tibetan). `focus: equal` synthesises across both. The `context` field carries a tiny glossary to anchor terminology.
- **`primary-search-semantic.json`** — semantic search in English against the Tibetan corpus. Best general-purpose mode; uses an English vector pivot internally.
- **`primary-search-regular.json`** — lexical-only search for an exact Sanskrit phrase. Use this mode for proper-name searches and verbatim lookups.
- **`primary-search-by-segmentnr.json`** — direct passage lookup. `search_input` is required by the schema even though it's ignored when `segmentnr` is set; pass the segmentnr itself as a placeholder.
- **`nexus-matches.json`** — body for `nexus.sh matches`: a list of `segment_nrs` whose precomputed parallels you want. `--agg` collapses them to per-target-text counts.
- **`nexus-table.json`** — body for `nexus.sh table`: a `filename` plus the full filter block (min `par_length`/`score`, language and include/exclude file/category/collection lists) and `skip_pagination: true`, which makes the endpoint return the complete intersection in one response. The convenience flags on `nexus.sh table` build this body (and set `skip_pagination`) for you; the file is here as a template.
