#!/usr/bin/env bash
# primary-search.sh — POST a JSON body to DharmaMitra's /primary/ search endpoint.
#
# Searches canonical Buddhist corpora (Kangyur/Tengyur, Taishō, Pali Nikāyas,
# Sanskrit critical editions). Returns matched passages with segmentnr IDs and
# deep-links into the DharmaMitra reading room. Typical latency 0.3–3 s.
#
# Rate limit: 400 req/day per IP. Use max_depth: 30 for agent use unless the
# user explicitly asks to scan wide — 200 is the browser-UI default and wastes
# the LLM's attention budget.
#
# Usage:
#   echo '{"search_input":"...", ...}' | ./scripts/primary-search.sh
#   ./scripts/primary-search.sh --file body.json
#   ./scripts/primary-search.sh --file body.json --trim    # strip vector + text_new
#
# Body schema (see CLAUDE.md for full reference):
#   search_input                          required, string
#   search_type                           "semantic" (default) | "regular" | "semantic_only"
#   filter_source_language                "auto" | "bo" | "sa" | "zh" | "pa" | "all"
#   filter_target_language                same set; default "all"
#   max_depth                             int; prefer 30 for agent use
#   source_filters.segmentnr              direct lookup (search_input ignored)
#   source_filters.include_files          list of work IDs
#   source_filters.include_categories     list of category names
#   source_filters.include_collections    list of collection names

set -euo pipefail

ENDPOINT="${DHARMAMITRA_PRIMARY_URL:-https://dharmamitra.org/api-search/primary/}"
BODY_FILE=""
TRIM=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)     BODY_FILE="$2"; shift 2 ;;
    --endpoint) ENDPOINT="$2"; shift 2 ;;
    --trim)     TRIM=1; shift ;;
    -h|--help)  sed -n '2,27p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "primary-search.sh: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -n "$BODY_FILE" ]]; then
  RESPONSE=$(curl -sS --max-time 60 -X POST "$ENDPOINT" \
    -H 'Content-Type: application/json' \
    --data-binary "@$BODY_FILE")
else
  RESPONSE=$(curl -sS --max-time 60 -X POST "$ENDPOINT" \
    -H 'Content-Type: application/json' \
    --data-binary @-)
fi

if [[ "$TRIM" -eq 1 ]]; then
  if ! command -v jq >/dev/null 2>&1; then
    echo "primary-search.sh: --trim requires jq" >&2
    exit 3
  fi
  printf '%s' "$RESPONSE" | jq '{results: (.results | map({segmentnr, lang, source, title, text, summary, src_link}))}'
else
  printf '%s\n' "$RESPONSE"
fi
