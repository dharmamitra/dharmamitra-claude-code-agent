#!/usr/bin/env bash
# trim-primary.sh — strip heavy fields from a primary-search response.
#
# Reads a /primary/ JSON response on stdin and emits a slimmed version with:
#   - vector field removed (768+ floats per hit)
#   - text_new removed (overlaps with text)
#
# Use this before feeding results to an LLM context.
#
# Usage:
#   cat raw.json | ./scripts/trim-primary.sh
#   ./scripts/primary-search.sh --file body.json | ./scripts/trim-primary.sh

set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "trim-primary.sh: requires jq" >&2
  exit 3
fi

jq '{results: (.results | map({segmentnr, all_segmentnrs, lang, source, title, text, summary, src_link}))}'
