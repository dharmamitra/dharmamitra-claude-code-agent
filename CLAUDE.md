# DharmaMitra Agent Starterpack — Project Context

This folder is a starter project for using Claude Code with the **DharmaMitra**
API to do two things on classical Asian Buddhist texts:

1. **Translation** — multi-witness machine translation of canonical passages
   (Tibetan, Chinese, Pali, Sanskrit → English / German / …) with the user's
   own reference translations and glossaries threaded in as context.
2. **Philology / critical editions** — using cross-language parallel retrieval
   to surface variant readings, suggest emendations, and build a critical
   apparatus around a passage.

A user typically arrives with: a source text in one or more canon languages,
optional reference translations of the same or related works, and a goal
(translate this whole sūtra; build an apparatus around chapter 5; etc.).

Your job is to drive the DharmaMitra API on their behalf — chunking, threading
context, citing properly, and writing structured output to disk.

---

## The two endpoints

Both POST, both JSON, both unauthenticated. Call via the wrapper scripts —
they're already on PATH-shape and handle timeouts:

- `./scripts/cat-translate.sh` → `POST /cat-translate/v1/translate` — multi-source synthesised translation
- `./scripts/primary-search.sh` → `POST /primary/` — canonical corpus search

Pipe the JSON body in on stdin, or pass `--file body.json`. Add `--trim` to
`primary-search.sh` to strip the heavy `vector` and `text_new` fields before
feeding results to a model.

### 1. cat-translate — multi-source canonical translation

Use when: the user has the same passage in two or more of the four canon
languages and wants one synthesised translation that weighs the witnesses
against each other. Works with one witness too, but single-source quick
translation has lighter-weight endpoints elsewhere — only use this one when
you actually want the multi-source synthesis or the per-language search-augmented
prompt.

**Do not use** for: single-word glosses (use a dictionary), OCR, or transliteration.

Body fields (all `input_*` default to `""`; at least one must be non-empty):

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `input_tibetan` | string | `""` | Unicode or Wylie |
| `input_chinese` | string | `""` | Classical Chinese |
| `input_pali` | string | `""` | IAST / Roman |
| `input_sanskrit` | string | `""` | Devanagari or IAST |
| `context` | string | `""` | Glossary, prior sentences, register notes — anything the model should know first |
| `focus` | enum | `"equal"` | `equal` \| `tibetan` \| `chinese` \| `pali` \| `sanskrit` |
| `target_language` | string | `"english"` | Free-form label, **not** ISO. `"english"`, `"german"`, `"modern chinese"`, `"french"` |
| `style_instruction` | string | `"balanced"` | Read **verbatim** by the model — write it like an instruction to a human translator |

Response: `{"translation": "<text>"}`. No metadata, no per-witness breakdown.

**Style instruction templates** — pick or adapt one:

- `"balanced"` — fluent but faithful, light parenthetical glosses.
- `"hyper-literal: preserve every Sanskrit compound, give the original term in parentheses on first occurrence, no editorial smoothing"`
- `"fluent and readable, modern English prose, omit technical glosses, suitable for a general reader"`
- `"academic register, IAST for Sanskrit names, footnote-style bracketed insertions for clarifications"`
- `"matches the published Reading Room translations of the Tibetan canon"`

**Latency**: 3–8 s typical, up to ~60 s for long inputs. Don't set `--max-time`
below 90 s. Cloudflare upstream caps at 100 s → 524.

**Rate limit (cat-translate)**: per-IP 200/min, 8 000/day. Generous for normal
use; not something to worry about during a translation pass.

### 2. /primary/ — canonical corpus search

Use when: the user wants to find passages in the canonical Buddhist corpus
(Kangyur, Tengyur, Taishō, Pali Nikāyas, Sanskrit critical editions) by
meaning or by exact text. Returns matched passages with canonical segment IDs
and deep-links into the DharmaMitra reading room.

Body fields:

| Field | Type | Default | Notes |
| --- | --- | --- | --- |
| `search_input` | string | **required** | Query in any canon language, English, or romanized form |
| `input_encoding` | enum | `"auto"` | `auto` \| `tibetan` \| `wylie` \| `dev` \| `iast` \| `hk` |
| `search_type` | enum | `"semantic"` | `regular` \| `semantic` \| `semantic_only` — see below |
| `semantic_type` | enum | `"both"` | `paragraph` \| `both`. Rarely worth changing. |
| `filter_source_language` | enum | `"auto"` | `auto` \| `bo` \| `sa` \| `zh` \| `pa` \| `all` |
| `filter_target_language` | enum | `"all"` | Same set. Restricts the matched parallels' language. |
| `source_filters` | object | `null` | See below |
| `do_ranking` | bool | `true` | **For agent use, pass `false`** — the final ranker is tuned for the browser UI; we don't need it for LLM consumption |
| `max_depth` | int | `200` | **For agent use, pass `30`** — 200 is tuned for the browser-UI pagination |

`source_filters` (all optional):

```json
{
  "include_files":       ["BO_K01_D0006"],
  "include_categories":  ["vinaya", "sutra"],
  "include_collections": ["kangyur", "tengyur"],
  "segmentnr":           "BO_K01_D0006:42b-3"
}
```

Passing `segmentnr` is a direct lookup; `search_input` is ignored but the
field is still required (pass the segmentnr as a placeholder).

**Choosing `search_type`:**

- `semantic` (default) — lexical + vector via English pivot. Best general-purpose mode.
- `regular` — lexical only. Use for proper-name searches, exact phrase lookups, anything the user typed expecting verbatim hits.
- `semantic_only` — skips lexical. Use when the query script doesn't match the filter language (e.g. Wylie query against Sanskrit-only filter) — the lexical path produces false positives there.

If unsure: default to `semantic`. Noisy → retry with `regular`. Cross-script
query → escalate to `semantic_only`.

**Response shape** (one hit):

```json
{
  "segmentnr":      "BO_K01_D0006:42b-3",
  "all_segmentnrs": ["BO_K01_D0006:42b-3", "BO_K01_D0006:42b-4"],
  "lang":           "bo",
  "source":         "BO_K01_D0006",
  "title":          "འདུལ་བ་གཞི། (Vinayavastu)",
  "text":           "<matched passage>",
  "summary":        "...",
  "src_link":       "https://dharmamitra.org/nexus/db/bo/BO_K01_D0006/text?active_segment=BO_K01_D0006:42b-3",
  "text_new":       { "...": "overlaps with .text" },
  "vector":         [/* 768+ floats */]
}
```

**Always strip `vector` and `text_new`** before passing results to a model.
The `--trim` flag on `primary-search.sh` does this for you, or pipe through
`./scripts/trim-primary.sh`.

`segmentnr` prefixes are reliable: `BO_` Tibetan, `SA_` Sanskrit, `PA_` Pali,
`ZH_` Chinese. Use `src_link` verbatim when citing — don't construct your own
URL.

**Rate limit (primary)**: 400 req/day per IP, 500/day per /24 subnet. This is
the real practical ceiling — budget your searches. For an agent doing
follow-up queries on emendations, 30–50 well-chosen searches in a session is
fine; spraying 200 queries through the day will burn the quota.

---

## Workflows

### Translation — the "translator mill"

The headline workflow is a translator mill: page by page through a long
document, where each API call's `context` field carries forward the user's
existing translation of *this* document so terminology, register, and voice
stay coherent across hundreds of pages. The `context` field is what makes this
work; treat it as a first-class input, not a metadata slot.

1. **Locate sources & references.**
   - Source(s): typically a file under `sources/`, possibly in multiple canon languages (one file per language, named `<work>.<lang>.txt`). Or text the user pasted.
   - References: scan `references/` for prior translations (especially any partial translation of *this* work the user has already done), glossaries, named-entity lists, register notes. Plain text and Markdown work directly. For .docx, .pdf, .epub, use the **reference-reader** subagent to extract them first.
2. **Build a translation brief.** Distil from the references: target language, register/style, terminology choices (Skt. *dharma* → "Dharma" not "phenomena", etc.), proper names. Write the brief to `output/translations/<work>.brief.md` so subsequent passes can re-read it.
3. **Chunk the source.** Aim for **3–5 sentences (~80–150 source words) per chunk**. Break on sentence boundaries. If the text has natural units (śloka, gāthā, sūtra section markers), use those. Never cut mid-sentence.
4. **Iterate — the mill.** For each chunk, POST to cat-translate with:
   - All available `input_*` witnesses for that chunk.
   - `context`: built in priority order (cap ~400 words):
     1. **Rolling prior translation of this document** — the last ~1–2 pages (3–5 chunks) you already produced into `output/translations/<work>.md`. Quote as translated prose. This is what makes each chunk read as if written by the same translator as the previous one.
     2. **User-supplied prior translation of this work**, if any reference file covers passages adjacent to the current chunk. Gold when available.
     3. **Glossary entries** for terms in the current chunk.
     4. **Named-entity decisions** relevant here.
     5. **One-sentence register reminder**, if room remains.
     If you have to drop items, drop from the bottom — rolling prior translation outranks glossary, because glossary is implicit in any prior translation that uses those terms.
   - `focus`: `"equal"` unless the user nominated a base text.
   - `style_instruction`: the style line from the brief (write it verbatim — the model reads it as instruction).
5. **Append, don't rewrite.** Write to `output/translations/<work>.md` incrementally: each chunk as source-then-translation, with a small header noting model parameters. The translator agent rereads this file on the next chunk to build the rolling context — so don't rewrite the format mid-run.
6. **Pause every ~5 chunks** to report progress and let the user adjust terminology or style before drift compounds. Translation drift is the single biggest failure mode of long-running translation runs — short feedback loops are cheap. When the user corrects terminology mid-run, *write the correction into the brief* before resuming so the next context build picks it up.

### Philology / critical edition

1. **Anchor passage.** User points to a passage (paste or `sources/<work>:lines`). If it has multiple language witnesses, note them all.
2. **Find parallels.** Call `/primary/` with the passage text:
   - `search_type: "semantic"` first.
   - `filter_source_language: "all"` (or `"auto"` if the script is unambiguous).
   - `max_depth: 30`. Bump to 50 only if the user asks to scan widely.
   - Pipe through `--trim` or `trim-primary.sh`.
3. **Triage hits.** Group by `source`/`title`. The same canonical passage will often appear in several collections (e.g. a verse cited in a commentary). Note `segmentnr` and `src_link` for citation.
4. **Compare witnesses.** For each parallel, line up against the anchor. Flag:
   - **Variant readings** — same place in text, different wording. Quote both, cite both segmentnrs.
   - **Possible emendations** — readings where one witness is clearly better-fitting (meter, grammar, sense, attestation by a translation). Write the emendation explicitly: "read X for Y, supported by Z".
   - **Lacunae / pluses** — missing or added material in one branch.
5. **Drill in on suspect words.** If a single word looks corrupt, do a follow-up `/primary/` with `search_type: "regular"` and that word (or its likely original form) as `search_input`. Restrict by language if you can.
6. **Optional: stylised back-translation.** For each variant, run `cat-translate` with `focus` set to that witness's language and `style_instruction: "hyper-literal: preserve every compound, give the original term in parentheses on first occurrence, no editorial smoothing"`. This is what the witness *says*, in English, for the apparatus.
7. **Write the apparatus.** Output to `output/critical-editions/<work>.md`. One section per anchor passage, with: anchor text, parallels list (segmentnr + src_link), variants table, emendations proposed, notes.

### Direct segment lookup

`/primary/` with `source_filters.segmentnr` set. `search_input` must still be
present (Pydantic requires it) — pass the segmentnr itself as the placeholder.
Use this when you have a citation and want the surrounding text. Note: this
endpoint returns the matched segment only, not adjacent context. For
before/after, you'd need a passage-detail endpoint that isn't in this kit.

---

## Defaults you should follow

- Chunk size for translation: **3–5 sentences**, ~80–150 source words.
- `max_depth` on `/primary/`: **30** for agent use. Bump only on explicit request.
- `do_ranking` on `/primary/`: **`false`** for agent use. The ranker is browser-UI-tuned; an LLM consuming the raw hits doesn't need it and skipping it is faster.
- `focus`: **`equal`** unless the user nominates a base text.
- `style_instruction`: derive from the user's brief, or default to `"balanced"`. Write it as prose, not as a tag.
- `target_language`: always a label string (`"english"`, not `"en"`).
- Always pipe `/primary/` responses through `--trim` before reading the JSON — the `vector` field will otherwise wreck your context window.
- Cite using the returned `src_link`. Don't construct DharmaMitra URLs.

## Anti-patterns

- Don't translate a 5 000-word chapter in one cat-translate call. The synthesis is multi-source per call, not a chunker.
- Don't set `--max-time` below 90 s.
- Don't drop `max_depth` to `200` just because that's the API default — for LLM consumption it's wasteful.
- Don't lose the per-witness segmentnr when citing — that's the philological audit trail.
- Don't strip `summary` from `/primary/` results before triage; it's often the only signal that a hit is a quotation in a commentary vs. the canonical text itself.

## Folder layout

```
.claude/
  agents/        — specialised subagents (translator, philologist, …)
  commands/      — slash commands (/translate, /find-parallels, …)
  settings.json  — permissions allowlist for scripts + jq
scripts/         — wrapper scripts for the two endpoints
sources/         — user drops source texts here (one file per language)
references/      — user drops reference translations, glossaries, style guides
output/          — your written output: translations/, critical-editions/
examples/        — sample request bodies for both endpoints
```

When the user opens this folder for the first time and asks "what can you do
here?", point them at `README.md` and offer to walk through `examples/`.
