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
```

The translation call takes 3–8 seconds. Search calls take 0.3–3 seconds.

## What each example demonstrates

- **`cat-translate-sutra-opening.json`** — the classic "thus have I heard" opening, given as two witnesses (Sanskrit + Tibetan). `focus: equal` synthesises across both. The `context` field carries a tiny glossary to anchor terminology.
- **`primary-search-semantic.json`** — semantic search in English against the Tibetan corpus. Best general-purpose mode; uses an English vector pivot internally.
- **`primary-search-regular.json`** — lexical-only search for an exact Sanskrit phrase. Use this mode for proper-name searches and verbatim lookups.
- **`primary-search-by-segmentnr.json`** — direct passage lookup. `search_input` is required by the schema even though it's ignored when `segmentnr` is set; pass the segmentnr itself as a placeholder.
