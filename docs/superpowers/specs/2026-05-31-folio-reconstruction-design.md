# Folio Reconstruction Workflow — Design Spec

**Date:** 2026-05-31
**Status:** Approved

---

## Overview

A `/reconstruct <path>` slash command that takes a single Sanskrit folio with `…` marking lacunae and produces a combined philological report: classification of the text, corpus parallels, reconstructed Sanskrit (attested + proposed), and a full English translation.

The proponent is always Buddhist (Madhyamaka, Yogācāra, or Pramāṇa tradition). The text is philosophical prose or verse with at least one presupposed opponent. Ontological or epistemological content.

---

## Architecture

Three sequential stages. Stages 1 and 2 run in parallel; their outputs merge before Stage 3 begins.

```
Input folio (sources/<file>.txt)
        │
        ├──────────────────────────────┐
        ▼                              ▼
[Classification agent]      [Corpus search agent]
 - identify Buddhist school  - /primary/ semantic search
 - identify opponent          on surviving text fragments
 - topic, register,           - /primary/ regular search
   key technical terms          on technical terms
 - lacuna inventory           - cross-language search
        │                              │
        └──────────────┬───────────────┘
                       ▼
              [Synthesis + Reconstruction]
               - merge classification + hits
               - propose Sanskrit for each …
               - confidence label per gap
               - validation search on reconstructions
                       │
                       ▼
              [Translation via cat-translate]
                       │
                       ▼
          output/reconstructions/<work>.md
```

---

## Stage 1: Classification Agent (parallel)

Receives the raw folio text (with `…` intact). Produces a structured classification block passed to both synthesis and corpus search.

Analyzes for:

- **Buddhist school** — Madhyamaka, Yogācāra, Pramāṇa (Dignāga/Dharmakīrti lineage), or mixed/uncertain
- **Opponent** — inferred from refuted positions (e.g. Mīmāṃsā if *śabdanityatva* is attacked, Nyāya/Vaiśeṣika if *padārtha* categories are targeted, Sāṃkhya if *prakṛti* is in play)
- **Topic** — ontological (svabhāva, śūnyatā, sattā, kṣaṇikatva) or epistemological (pramāṇa, pratyakṣa, anumāna, apoha)
- **Register and form** — kārikā verse (with meter identified if possible), bhāṣya prose, or mixed
- **Key technical terms** — extracted verbatim, passed to corpus search as search tokens
- **Lacuna inventory** — count, position, and estimated akṣara length of each `…` (inferred from surrounding meter or syntax where possible)

Output format: compact structured block (not a prose paragraph), so it can be embedded directly in subsequent prompts.

---

## Stage 2: Corpus Search Agent (parallel)

Receives the same raw folio text plus the classification block once available (or runs with raw text alone if classification is still in progress). Uses `./scripts/primary-search.sh --trim` for all calls. Always sets `do_ranking: false`, `max_depth: 30`.

**Three search passes:**

1. **Semantic search on surviving text** — longest coherent surviving fragment as `search_input`; `search_type: "semantic"`; `filter_source_language: "sa"` first, then `"all"` if hits are sparse.

2. **Regular search on technical terms** — one call per distinctive term extracted by classification (e.g. *apoha*, *svabhāva*, *kṣaṇabhaṅga*); `search_type: "regular"`; `filter_source_language: "sa"`.

3. **Cross-language semantic search** — `filter_source_language: "all"`, `filter_target_language: "all"`. Catches Tibetan or Chinese translations that may independently confirm a reading.

Hits are kept only if `summary` indicates genuine parallel content. Grouped by `source`/`title`. `src_link` preserved verbatim for all retained hits.

---

## Stage 3: Synthesis and Reconstruction

Receives classification block + corpus hits. Works through each `…` lacuna in order.

**Per lacuna:**

1. **Context assessment** — grammatical constraints (expected case, verb, syntactic slot), metrical constraints (missing feet and prosodic shape), thematic constraints (what the argument requires).

2. **Parallel-informed reconstruction** — if a corpus hit overlaps with surrounding text, extract the corresponding portion as a candidate. Multiple candidates from different witnesses listed separately.

3. **Claude-generated reconstruction** — where no parallel covers the gap, reconstruct from genre conventions, school vocabulary, and opponent context. Marked as generated.

4. **Confidence labels:**
   - `◆ Attested` — gap directly filled by a parallel passage
   - `◇ Probable` — parallel is nearby; reconstruction follows from it plus grammatical/metrical constraints
   - `○ Speculative` — no parallel; reconstruction based on context and convention only

5. **Validation search** — `◇ Probable` and `○ Speculative` reconstructions get a `/primary/` regular search on the proposed Sanskrit phrase. A hit upgrades the label.

---

## Translation

Full folio text (attested + reconstructed, with `⟨...⟩` marking reconstructed portions) passed to `./scripts/cat-translate.sh` as `input_sanskrit`.

- `focus`: `"equal"`
- `target_language`: `"english"`
- `style_instruction`: `"academic register, IAST for Sanskrit technical terms on first occurrence, render ⟨reconstructed⟩ portions in [square brackets] in the translation to distinguish them from attested text, scholarly prose"`
- `context`: classification block (school, opponent, topic)

---

## Output Report

Written to `output/reconstructions/<filename>.md`.

```
# Folio Reconstruction: <filename>

## 1. Classification
School, opponent, topic, register, meter (if detected).

## 2. Corpus Parallels
Per hit: title, segmentnr, relevant excerpt, src_link.
Grouped by source text.

## 3. Reconstructed Folio
Full text with attested portions in roman,
reconstructed portions marked ⟨like this⟩,
confidence label after each gap.

## 4. Translation
Full folio in English.
Reconstructed portions in [square brackets].

## 5. Lacuna Notes
One entry per gap: position, akṣara estimate,
candidates considered, rationale for chosen reading.
```

---

## Implementation

- **Command file:** `.claude/commands/reconstruct.md`
- **Output directory:** `output/reconstructions/` (create if absent)
- **Scripts used:** `./scripts/primary-search.sh --trim`, `./scripts/cat-translate.sh`
- **Parallel dispatch:** classification and corpus search agents launched simultaneously via the dispatching-parallel-agents pattern

---

## Constraints

- Single folio scope only (this spec does not cover multi-folio runs)
- `max_depth: 30` on all `/primary/` calls; bump only on explicit user request
- `do_ranking: false` on all `/primary/` calls
- `--max-time 90` on all `cat-translate` calls (already set in script)
- `src_link` values cited verbatim from API response; never constructed manually
