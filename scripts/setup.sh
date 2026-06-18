#!/usr/bin/env bash
# setup.sh — one-time (and periodic) setup for this starter pack.
#
# Currently this builds the local corpus index that powers offline text identification
# (scripts/identify-text.py). Safe to run repeatedly; re-run it to refresh the cache.
#
# Usage:
#   ./scripts/setup.sh            # build the corpus index if missing or stale (> 30 days)
#   ./scripts/setup.sh --force    # rebuild the corpus index unconditionally
#
# The SessionStart hook in .claude/settings.json runs the staleness-checked variant of this
# automatically the first time you open the project (and refreshes it when the cache ages out),
# so manual runs are only needed to force an early refresh.

set -euo pipefail
cd "$(dirname "$0")/.."

echo "setup: checking prerequisites…"
for bin in python3 curl jq; do
  if command -v "$bin" >/dev/null 2>&1; then
    echo "  ✓ $bin"
  else
    echo "  ✗ $bin  (required — please install)" >&2
  fi
done

if [[ "${1:-}" == "--force" ]]; then
  echo "setup: rebuilding corpus index (forced)…"
  python3 scripts/build-corpus-index.py --force
else
  echo "setup: building corpus index if missing or older than 30 days…"
  python3 scripts/build-corpus-index.py --max-age-days 30
fi

echo "setup: done."
