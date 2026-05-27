#!/usr/bin/env bash
# cat-translate.sh — POST a JSON body to DharmaMitra's catena-translate endpoint.
#
# The endpoint synthesises a single translation from one or more canon-language
# witnesses (Tibetan, Chinese, Pali, Sanskrit). Synchronous; takes 3–8 s typical,
# up to ~60 s for long inputs. Do not lower the timeout.
#
# Usage:
#   echo '{"input_sanskrit":"...", ...}' | ./scripts/cat-translate.sh
#   ./scripts/cat-translate.sh --file body.json
#   ./scripts/cat-translate.sh --file body.json --pretty
#
# Body schema (all input_* default to ""; at least one must be non-empty):
#   input_tibetan, input_chinese, input_pali, input_sanskrit  string
#   context                                                   string
#   focus                                                     "equal" | "tibetan" | "chinese" | "pali" | "sanskrit"
#   target_language                                           free-form label ("english", "german", "modern chinese", ...)
#   style_instruction                                         free-form prose; read verbatim by the model
#
# Response: {"translation": "..."}

set -euo pipefail

ENDPOINT="${DHARMAMITRA_CAT_TRANSLATE_URL:-https://dharmamitra.org/api-search/cat-translate/v1/translate}"
BODY_FILE=""
PRETTY=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --file)     BODY_FILE="$2"; shift 2 ;;
    --endpoint) ENDPOINT="$2"; shift 2 ;;
    --pretty)   PRETTY=1; shift ;;
    -h|--help)  sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "cat-translate.sh: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -n "$BODY_FILE" ]]; then
  RESPONSE=$(curl -sS --max-time 90 -X POST "$ENDPOINT" \
    -H 'Content-Type: application/json' \
    --data-binary "@$BODY_FILE")
else
  RESPONSE=$(curl -sS --max-time 90 -X POST "$ENDPOINT" \
    -H 'Content-Type: application/json' \
    --data-binary @-)
fi

if [[ "$PRETTY" -eq 1 ]] && command -v jq >/dev/null 2>&1; then
  printf '%s' "$RESPONSE" | jq .
else
  printf '%s\n' "$RESPONSE"
fi
