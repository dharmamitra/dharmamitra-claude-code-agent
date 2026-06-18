# data/

Generated cache, not source data. **Do not edit by hand.**

- `corpus-index.json` — a flattened, diacritics-folded copy of the DharmaNexus corpus map
  (`/api-db/menudata/` for `sa`, `bo`, `zh`, `pa`), built by `scripts/build-corpus-index.py`
  and read by `scripts/identify-text.py` to resolve a human description to a corpus filename
  without a network call.

This file is `.gitignored`. It is built automatically on first session by the `SessionStart`
hook in `.claude/settings.json`, refreshed when it ages past 30 days, and can be rebuilt any
time with `./scripts/setup.sh --force`.
