#!/usr/bin/env bash
# nexus.sh — DharmaNexus intertextuality API (api-db).
#
# Three subcommands over https://dharmamitra.org/api-db :
#
#   matches   POST /matches/            — every stored parallel for a set of segmentnrs
#   menu      GET  /menudata/           — the corpus map for one language (collections → categories → files)
#   table     POST /table-view/table/   — a file's full intertextual intersection with the rest of the corpus,
#                                          with rich include/exclude filters
#
# These complement /primary/ search (scripts/primary-search.sh). /primary/ finds passages by meaning;
# DharmaNexus tells you, once you HAVE a passage or a whole text, exactly what else in the canon it
# overlaps with, segment by segment, across languages.
#
# To resolve a human description ("Yaśomitra's Abhidharma commentary") to a filename, use the
# local matcher instead of any live call:  ./scripts/identify-text.py "yasomitra abhidharma"
# (it reads the cached corpus index built by scripts/setup.sh). Feed the winning `filename`
# straight into `table`, or its segmentnrs into `matches`.
#
# ── matches ──────────────────────────────────────────────────────────────────
#   ./scripts/nexus.sh matches SA_K02_sspp2_3u:7287 SA_K02_sspp2_3u:7288
#   ./scripts/nexus.sh matches --file segnrs.json          # body = {"segment_nrs":[...]}
#   echo '{"segment_nrs":["..."]}' | ./scripts/nexus.sh matches
#   ./scripts/nexus.sh matches --agg SA_K02_sspp2_3u:7287  # collapse to per-target-text counts
#   ./scripts/nexus.sh matches --raw ...                   # keep offsets + nesting, no trim
#   Default output trims each match to: id, root_segnr, par_segnr, score, par_length, root_text,
#   par_text, par_text_name, par_display. --raw keeps everything (offsets etc.).
#
# ── menu ─────────────────────────────────────────────────────────────────────
#   ./scripts/nexus.sh menu sa            # lang ∈ sa | bo | zh | pa
#   ./scripts/nexus.sh menu sa --raw      # keep raw_metadata + search_field blobs
#   ./scripts/nexus.sh menu sa --meta SA_K01_bsu046_u   # print one file's raw_metadata markdown
#                                                       # (date estimate, AI summary, related works, links)
#   Default output is the compact tree: collection → category → {displayName, filename}.
#   Use the filename values as the `filename` / include_files / exclude_files arguments to `table`.
#
# ── table ────────────────────────────────────────────────────────────────────
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --agg --all          # COMPLETE per-target-text summary
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --agg                 # summary of page 0 only (quick survey)
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --include-files SA_K03_psp_2-3u --all  # vs. one text, all rows
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --include-collections kangyur --languages bo
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --par-length 50 --score 70 --sort length
#   ./scripts/nexus.sh table --file body.json                      # full body on stdin/--file
#   Flags: --par-length N (min, default 30) --score N (min, default 0) --languages a,b (default all)
#          --include-files / --exclude-files / --include-categories / --exclude-categories /
#          --include-collections / --exclude-collections  (each comma-separated)
#          --page N (default 0; 100 rows/page) --sort position|length (default position)
#          --folio STR  --agg  --raw  --all
#   PAGINATION MATTERS: the API returns 100 rows/page. A plain call (and --agg over it) sees ONLY that
#   page — for a whole-corpus table that is a partial survey, and a rare target may not appear at all.
#   Use --all to auto-paginate to completion (use it for any "does A relate to B / how much" question,
#   especially with --agg or --include-files). The include/exclude/score/par-length filters are applied
#   SERVER-SIDE — prefer them over fetching everything and filtering locally. Filter values are
#   exact-match: a wrong filename silently yields 0 rows (a false negative), so confirm IDs first.

set -euo pipefail

BASE="${DHARMAMITRA_DB_URL:-https://dharmamitra.org/api-db}"

need_jq() {
  command -v jq >/dev/null 2>&1 || { echo "nexus.sh: requires jq" >&2; exit 3; }
}

usage() { sed -n '2,54p' "$0" | sed 's/^# \{0,1\}//'; }

SUB="${1:-}"; [[ $# -gt 0 ]] && shift || true

case "$SUB" in
# ─────────────────────────────────────────────────────────────────────────────
matches)
  need_jq
  AGG=0; RAW=0; BODY_FILE=""; SEGS=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agg)  AGG=1; shift ;;
      --raw)  RAW=1; shift ;;
      --file) BODY_FILE="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      -*) echo "nexus.sh matches: unknown flag: $1" >&2; exit 2 ;;
      *)  SEGS+=("$1"); shift ;;
    esac
  done

  if [[ ${#SEGS[@]} -gt 0 ]]; then
    BODY=$(printf '%s\n' "${SEGS[@]}" | jq -R . | jq -s '{segment_nrs: .}')
  elif [[ -n "$BODY_FILE" ]]; then
    BODY=$(cat "$BODY_FILE")
  else
    BODY=$(cat -)
  fi

  RESP=$(curl -sS --max-time 90 -X POST "$BASE/matches/" \
    -H 'accept: application/json' -H 'Content-Type: application/json' \
    --data-binary "$BODY")

  if [[ "$AGG" -eq 1 ]]; then
    printf '%s' "$RESP" | jq '.matches
      | group_by(.par_full_names.text_name)
      | map({text: .[0].par_full_names.text_name,
             display: .[0].par_full_names.display_name,
             parallels: length,
             max_score: (map(.score) | max),
             total_par_length: (map(.par_length) | add)})
      | sort_by(-.parallels)'
  elif [[ "$RAW" -eq 1 ]]; then
    printf '%s\n' "$RESP"
  else
    printf '%s' "$RESP" | jq '{matches: (.matches | map({
      id, root_segnr, par_segnr, score, par_length, root_text, par_text,
      par_text_name: .par_full_names.text_name,
      par_display:   .par_full_names.display_name}))}'
  fi
  ;;

# ─────────────────────────────────────────────────────────────────────────────
menu)
  need_jq
  LANG=""; RAW=0; META=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --raw)  RAW=1; shift ;;
      --meta) META="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      -*) echo "nexus.sh menu: unknown flag: $1" >&2; exit 2 ;;
      *)  LANG="$1"; shift ;;
    esac
  done
  [[ -n "$LANG" ]] || { echo "nexus.sh menu: need a language (sa|bo|zh|pa)" >&2; exit 2; }

  RESP=$(curl -sS --max-time 60 -X GET "$BASE/menudata/?language=$LANG" -H 'accept: application/json')

  if [[ -n "$META" ]]; then
    printf '%s' "$RESP" | jq -r --arg fn "$META" '
      .menudata[].categories[].files[] | select(.filename==$fn) | .raw_metadata' \
      | { read -r line && { printf '%s\n' "$line"; cat; } || echo "nexus.sh menu: file not found: $META" >&2; }
  elif [[ "$RAW" -eq 1 ]]; then
    printf '%s\n' "$RESP"
  else
    printf '%s' "$RESP" | jq '{menudata: (.menudata | map({
      collection, collectiondisplayname,
      categories: (.categories | map({
        category, categorydisplayname,
        files: (.files | map({displayName, filename}))}))}))}'
  fi
  ;;

# ─────────────────────────────────────────────────────────────────────────────
table)
  need_jq
  AGG=0; RAW=0; ALL=0; BODY_FILE=""; FILENAME=""
  PAR_LENGTH=30; SCORE=0; LANGS="all"; PAGE=0; SORT="position"; FOLIO=""
  INC_F=""; EXC_F=""; INC_CAT=""; EXC_CAT=""; INC_COL=""; EXC_COL=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agg)  AGG=1; shift ;;
      --raw)  RAW=1; shift ;;
      --all)  ALL=1; shift ;;
      --file) BODY_FILE="$2"; shift 2 ;;
      --par-length) PAR_LENGTH="$2"; shift 2 ;;
      --score) SCORE="$2"; shift 2 ;;
      --languages) LANGS="$2"; shift 2 ;;
      --page) PAGE="$2"; shift 2 ;;
      --sort) SORT="$2"; shift 2 ;;
      --folio) FOLIO="$2"; shift 2 ;;
      --include-files) INC_F="$2"; shift 2 ;;
      --exclude-files) EXC_F="$2"; shift 2 ;;
      --include-categories) INC_CAT="$2"; shift 2 ;;
      --exclude-categories) EXC_CAT="$2"; shift 2 ;;
      --include-collections) INC_COL="$2"; shift 2 ;;
      --exclude-collections) EXC_COL="$2"; shift 2 ;;
      -h|--help) usage; exit 0 ;;
      -*) echo "nexus.sh table: unknown flag: $1" >&2; exit 2 ;;
      *)  FILENAME="$1"; shift ;;
    esac
  done

  csv2json() { [[ -z "$1" ]] && echo '[]' || ( printf '%s' "$1" | jq -R 'split(",") | map(select(length>0))' ); }

  if [[ -n "$BODY_FILE" ]]; then
    BODY=$(cat "$BODY_FILE")
  elif [[ -z "$FILENAME" && -t 0 ]]; then
    echo "nexus.sh table: need a filename (or --file body.json / body on stdin)" >&2; exit 2
  elif [[ -z "$FILENAME" ]]; then
    BODY=$(cat -)
  else
    BODY=$(jq -n \
      --arg fn "$FILENAME" --argjson pl "$PAR_LENGTH" --argjson sc "$SCORE" \
      --argjson langs "$(csv2json "$LANGS")" \
      --argjson incf "$(csv2json "$INC_F")"  --argjson excf "$(csv2json "$EXC_F")" \
      --argjson incc "$(csv2json "$INC_CAT")" --argjson excc "$(csv2json "$EXC_CAT")" \
      --argjson inccol "$(csv2json "$INC_COL")" --argjson exccol "$(csv2json "$EXC_COL")" \
      --argjson page "$PAGE" --arg sort "$SORT" --arg folio "$FOLIO" \
      '{filename:$fn, filters:{par_length:$pl, score:$sc, languages:$langs,
        include_files:$incf, exclude_files:$excf,
        include_categories:$incc, exclude_categories:$excc,
        include_collections:$inccol, exclude_collections:$exccol},
        page:$page, sort_method:$sort, folio:$folio}')
  fi

  # fetch_page <page> <outfile> → writes body to outfile, echoes HTTP status code.
  fetch_page() {
    local b
    b=$(printf '%s' "$BODY" | jq --argjson pg "$1" '.page = $pg')
    curl -sS -o "$2" -w '%{http_code}' --max-time 90 -X POST "$BASE/table-view/table/" \
      -H 'accept: application/json' -H 'Content-Type: application/json' \
      --data-binary "$b"
  }

  if [[ "$ALL" -eq 1 ]]; then
    # Auto-paginate (100 rows/page) until a short page — so --agg is a census, not just page 0.
    # The endpoint rate-limits (HTTP 429) under rapid sequential calls, so pace requests and
    # back off exponentially. Accumulate rows as JSONL; never put page-sized JSON on argv.
    TMPD=$(mktemp -d "${TMPDIR:-/tmp}/nexus-table.XXXXXX")
    trap 'rm -rf "$TMPD"' EXIT
    ROWS="$TMPD/rows.jsonl"; : > "$ROWS"
    PGF="$TMPD/page.json"
    p="$PAGE"; pages=0
    while :; do
      ok=0; delay=1
      for _try in 1 2 3 4 5; do
        code=$(fetch_page "$p" "$PGF" || echo 000)
        if [[ "$code" == "200" ]] && jq -e 'type=="array"' "$PGF" >/dev/null 2>&1; then ok=1; break; fi
        sleep "$delay"; delay=$((delay * 2))   # 1,2,4,8s backoff (mostly for 429)
      done
      if [[ "$ok" -eq 0 ]]; then
        echo "nexus.sh table: page $p failed after retries (last HTTP $code) — returning partial result ($(wc -l < "$ROWS" | tr -d ' ') rows so far)" >&2
        break
      fi
      n=$(jq 'length' "$PGF")
      jq -c '.[]' "$PGF" >> "$ROWS"
      pages=$((pages + 1))
      { [[ "$n" -lt 100 ]] || [[ "$pages" -ge 100 ]]; } && break
      p=$((p + 1))
      sleep 0.4   # pace requests to stay under the endpoint's rate limit
    done
    [[ "$pages" -ge 100 ]] && echo "nexus.sh table: stopped at 100 pages (10k rows) — result may be truncated" >&2
    RESP=$(jq -s '.' "$ROWS")
  else
    RESP=$(curl -sS --max-time 90 -X POST "$BASE/table-view/table/" \
      -H 'accept: application/json' -H 'Content-Type: application/json' \
      --data-binary "$BODY")
  fi

  if [[ "$AGG" -eq 1 ]]; then
    printf '%s' "$RESP" | jq '
      group_by(.par_full_names.text_name)
      | map({text: .[0].par_full_names.text_name,
             display: .[0].par_full_names.display_name,
             tgt_lang: .[0].tgt_lang,
             parallels: length,
             max_score: (map(.score) | max),
             total_par_length: (map(.par_length) | add)})
      | sort_by(-.parallels)'
  elif [[ "$RAW" -eq 1 ]]; then
    printf '%s\n' "$RESP"
  else
    printf '%s' "$RESP" | jq 'map({
      root_segnr_range, par_segnr_range, score, root_length, par_length,
      src_lang, tgt_lang,
      par_text_name: .par_full_names.text_name,
      par_display:   .par_full_names.display_name,
      root_text: (.root_fulltext | map(.text) | join(" ")),
      par_text:  (.par_fulltext  | map(.text) | join(" "))})'
  fi
  ;;

# ─────────────────────────────────────────────────────────────────────────────
-h|--help|"")
  usage ;;
*)
  echo "nexus.sh: unknown subcommand: $SUB (expected: matches | menu | table)" >&2
  exit 2 ;;
esac
