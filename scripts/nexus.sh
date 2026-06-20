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
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --agg                # per-target-text summary (THE key view)
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --include-files SA_K03_psp_2-3u   # vs. one text only
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --include-collections kangyur --languages bo
#   ./scripts/nexus.sh table SA_K02_sspp2_3u --par-length 50 --score 70 --sort length
#   ./scripts/nexus.sh table SA_T07_vakobhau --not-after 350 --agg    # only parallels in texts dated ≤ 350 CE
#   ./scripts/nexus.sh table SA_T07_vakobhau --not-before 600 --agg   # only parallels in texts dated ≥ 600 CE
#   ./scripts/nexus.sh table --file body.json                      # full body on stdin/--file
#   Flags: --par-length N (min, default 30) --score N (min, default 0) --languages a,b (default all)
#          --include-files / --exclude-files / --include-categories / --exclude-categories /
#          --include-collections / --exclude-collections  (each comma-separated)
#          --not-before YEAR  --not-after YEAR   (CE; BCE negative — see below)
#          --sort position|length (default position)  --folio STR  --agg  --raw
#   COMPLETE BY DEFAULT: the request sets skip_pagination so the endpoint returns the WHOLE
#   intersection in one response — every call (and --agg over it) is a census, not a sample. The
#   complete table of a well-connected text can be many MB. The include/exclude/score/par-length
#   filters are applied SERVER-SIDE — prefer them over fetching everything and filtering locally;
#   they are exact-match, so a wrong filename silently yields 0 rows (a false negative). Confirm IDs.
#   DATE FILTERS (Sanskrit only): --not-before / --not-after restrict the matched PARALLELS to texts
#   whose date estimate falls in [not_before, not_after] (year CE; the bound is keyed to the
#   sanskrit-dating model). Powerful for DIRECTION OF BORROWING — e.g. to find only potential
#   *sources* of a text, restrict to parallels dated before it (--not-after <its date>); for its
#   *reception*, restrict to parallels after it (--not-before <its date>).

set -euo pipefail

BASE="${DHARMAMITRA_DB_URL:-https://dharmamitra.org/api-db}"

need_jq() {
  command -v jq >/dev/null 2>&1 || { echo "nexus.sh: requires jq" >&2; exit 3; }
}

usage() { sed -n '2,59p' "$0" | sed 's/^# \{0,1\}//'; }

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
  AGG=0; RAW=0; BODY_FILE=""; FILENAME=""
  PAR_LENGTH=30; SCORE=0; LANGS="all"; SORT="position"; FOLIO=""
  INC_F=""; EXC_F=""; INC_CAT=""; EXC_CAT=""; INC_COL=""; EXC_COL=""
  NOT_BEFORE=""; NOT_AFTER=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --agg)  AGG=1; shift ;;
      --raw)  RAW=1; shift ;;
      --file) BODY_FILE="$2"; shift 2 ;;
      --par-length) PAR_LENGTH="$2"; shift 2 ;;
      --score) SCORE="$2"; shift 2 ;;
      --languages) LANGS="$2"; shift 2 ;;
      --not-before) NOT_BEFORE="$2"; shift 2 ;;
      --not-after)  NOT_AFTER="$2"; shift 2 ;;
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

  # skip_pagination:true makes the endpoint return the COMPLETE intersection in one response
  # (no paging) — so a survey is always a census. Merge it into whatever body we send.
  if [[ -n "$BODY_FILE" ]]; then
    BODY=$(jq '. + {skip_pagination: true}' "$BODY_FILE")
  elif [[ -z "$FILENAME" && -t 0 ]]; then
    echo "nexus.sh table: need a filename (or --file body.json / body on stdin)" >&2; exit 2
  elif [[ -z "$FILENAME" ]]; then
    BODY=$(jq '. + {skip_pagination: true}')
  else
    BODY=$(jq -n \
      --arg fn "$FILENAME" --argjson pl "$PAR_LENGTH" --argjson sc "$SCORE" \
      --argjson langs "$(csv2json "$LANGS")" \
      --argjson incf "$(csv2json "$INC_F")"  --argjson excf "$(csv2json "$EXC_F")" \
      --argjson incc "$(csv2json "$INC_CAT")" --argjson excc "$(csv2json "$EXC_CAT")" \
      --argjson inccol "$(csv2json "$INC_COL")" --argjson exccol "$(csv2json "$EXC_COL")" \
      --arg nb "$NOT_BEFORE" --arg na "$NOT_AFTER" \
      --arg sort "$SORT" --arg folio "$FOLIO" \
      '{filename:$fn, filters:({par_length:$pl, score:$sc, languages:$langs,
        include_files:$incf, exclude_files:$excf,
        include_categories:$incc, exclude_categories:$excc,
        include_collections:$inccol, exclude_collections:$exccol}
        + (if $nb != "" then {not_before: ($nb|tonumber)} else {} end)
        + (if $na != "" then {not_after:  ($na|tonumber)} else {} end)),
        page:0, sort_method:$sort, folio:$folio, skip_pagination:true}')
  fi

  # The complete intersection of a well-connected text can be many MB — stream to a temp file
  # rather than holding it in a shell variable.
  TMPF=$(mktemp "${TMPDIR:-/tmp}/nexus-table.XXXXXX")
  trap 'rm -f "$TMPF"' EXIT
  code=$(curl -sS -o "$TMPF" -w '%{http_code}' --max-time 180 -X POST "$BASE/table-view/table/" \
    -H 'accept: application/json' -H 'Content-Type: application/json' \
    --data-binary "$BODY" || echo 000)
  if [[ "$code" != "200" ]] || ! jq -e 'type=="array"' "$TMPF" >/dev/null 2>&1; then
    echo "nexus.sh table: request failed (HTTP $code)" >&2
    head -c 300 "$TMPF" >&2; echo >&2
    exit 4
  fi

  if [[ "$AGG" -eq 1 ]]; then
    jq '
      group_by(.par_full_names.text_name)
      | map({text: .[0].par_full_names.text_name,
             display: .[0].par_full_names.display_name,
             tgt_lang: .[0].tgt_lang,
             parallels: length,
             max_score: (map(.score) | max),
             total_par_length: (map(.par_length) | add)})
      | sort_by(-.parallels)' "$TMPF"
  elif [[ "$RAW" -eq 1 ]]; then
    cat "$TMPF"; echo
  else
    jq 'map({
      root_segnr_range, par_segnr_range, score, root_length, par_length,
      src_lang, tgt_lang,
      par_text_name: .par_full_names.text_name,
      par_display:   .par_full_names.display_name,
      root_text: (.root_fulltext | map(.text) | join(" ")),
      par_text:  (.par_fulltext  | map(.text) | join(" "))})' "$TMPF"
  fi
  ;;

# ─────────────────────────────────────────────────────────────────────────────
-h|--help|"")
  usage ;;
*)
  echo "nexus.sh: unknown subcommand: $SUB (expected: matches | menu | table)" >&2
  exit 2 ;;
esac
