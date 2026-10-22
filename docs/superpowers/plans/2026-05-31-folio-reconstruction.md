# Folio Reconstruction Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/reconstruct <path>` slash command that takes a Sanskrit folio with `…` lacunae and produces a combined philological report: classification, corpus parallels, reconstructed Sanskrit, and English translation.

**Architecture:** Two agents (classifier, reconstructor) plus the existing corpus-searcher agent work in a parallel-then-synthesise pipeline. The command orchestrates them and writes structured output to `output/reconstructions/`. The existing `cat-translate.sh` and `primary-search.sh` scripts handle all API calls.

**Tech Stack:** Claude Code slash commands (`.claude/commands/`), Claude Code subagents (`.claude/agents/`), DharmaMitra `/primary/` endpoint, DharmaMitra `cat-translate` endpoint, bash + jq.

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `.claude/commands/reconstruct.md` | Slash command: reads input, dispatches parallel agents, synthesises, writes report |
| Create | `.claude/agents/classifier.md` | Identifies school, opponent, topic, technical terms, lacuna inventory |
| Create | `.claude/agents/reconstructor.md` | Proposes Sanskrit reconstructions with confidence labels; runs validation searches |
| Create | `sources/test-folio.txt` | Sample folio with lacunae for smoke testing |
| Create | `output/reconstructions/.gitkeep` | Ensures output directory is tracked in git |

The existing `.claude/agents/corpus-searcher.md` and `.claude/agents/translator.md` are reused as-is. No modifications needed.

---

### Task 1: Create output directory and test fixture

**Files:**
- Create: `output/reconstructions/.gitkeep`
- Create: `sources/test-folio.txt`

- [ ] **Step 1: Create the reconstructions output directory**

```bash
mkdir -p output/reconstructions
touch output/reconstructions/.gitkeep
```

- [ ] **Step 2: Create the test folio**

Write `sources/test-folio.txt` with this content — a plausible Dharmakīrti-style kṣaṇikavāda passage with four lacunae of varying length:

```
yat sat tat … arthakriyāsamartham |
tac ca kṣaṇikam iti … siddham |
na hi sthiraṃ vastu … kartuṃ śaknoti |
ataḥ … sattvam arthakriyāśaktir eva |
pūrvapakṣaḥ: nityam api … sāmarthyaṃ bhavet iti cet |
na, kṣaṇabhaṅge … siddhaḥ |
```

- [ ] **Step 3: Verify both files exist**

```bash
ls output/reconstructions/.gitkeep sources/test-folio.txt
```

Expected output:
```
output/reconstructions/.gitkeep
sources/test-folio.txt
```

- [ ] **Step 4: Commit**

```bash
git add output/reconstructions/.gitkeep sources/test-folio.txt
git commit -m "Add reconstructions output dir and test folio fixture"
```

---

### Task 2: Create the classifier agent

**Files:**
- Create: `.claude/agents/classifier.md`

- [ ] **Step 1: Write the classifier agent**

Write `.claude/agents/classifier.md` with this content:

```markdown
---
name: classifier
description: Analyse a Sanskrit folio (with … lacunae) to identify the Buddhist school, opponent, topic, register, key technical terms, and lacuna inventory. Produces a structured classification block for use by the reconstructor and corpus-searcher agents.
tools: Read, Bash, Glob
---

You receive a Sanskrit folio containing `…` markers for lacunae. Your job is to analyse the surviving text and produce a structured classification block. Be concise and precise; do not translate or reconstruct anything.

## Output format

Return ONLY the following block, filled in — no prose before or after:

```
CLASSIFICATION
==============
school:       <Madhyamaka | Yogācāra | Pramāṇa (Dignāga/Dharmakīrti) | mixed | uncertain>
opponent:     <Mīmāṃsā | Nyāya-Vaiśeṣika | Sāṃkhya | Jain | other Buddhist school | uncertain — briefly note the clue>
topic:        <ontological | epistemological | mixed — name the specific issue, e.g. "kṣaṇikavāda", "apoha theory", "svabhāva">
register:     <kārikā verse | bhāṣya prose | mixed — if verse, name meter if detectable>
possible_id:  <if the text strongly resembles a known work, name it; otherwise "unknown">
terms:        <comma-separated list of distinctive technical terms found verbatim in the surviving text>
lacunae:
  1. position: <brief description, e.g. "after yat sat tat"> | estimated_aksaras: <number or range, e.g. "3–5"> | syntactic_slot: <what grammatical element is expected>
  2. ...
  (one line per … in the order they appear)
```

## How to analyse

- **School:** Look for vocabulary associated with specific traditions. Pramāṇa: pramāṇa, pratyakṣa, anumāna, apoha, svalakṣaṇa, arthakriyā, kṣaṇika. Madhyamaka: svabhāva, śūnyatā, pratītyasamutpāda, niḥsvabhāva. Yogācāra: vijñaptimātra, ālayavijñāna, trisvabhāva, parikalpita.
- **Opponent:** Look for refuted positions. Śabdanityatva or apūrva → Mīmāṃsā. Padārtha categories, sāmānya, viśeṣa → Nyāya-Vaiśeṣika. Prakṛti, puruṣa → Sāṃkhya. Anekāntavāda → Jain. Explicit pūrvapakṣa markers are strong evidence.
- **Lacuna estimation:** In anuṣṭubh verse each pāda is 8 syllables; in śloka each half-verse is 16. Count surviving syllables in the line to estimate the gap. In prose, use surrounding syntax to estimate the number of missing words/compounds.
- **Syntactic slot:** State what grammatical role the missing text fills — subject, object, predicate, qualifier, etc.
```

- [ ] **Step 2: Verify the file exists and has correct frontmatter**

```bash
head -5 .claude/agents/classifier.md
```

Expected:
```
---
name: classifier
description: Analyse a Sanskrit folio (with … lacunae) to identify the Buddhist
```

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/classifier.md
git commit -m "Add classifier subagent for folio reconstruction"
```

---

### Task 3: Create the reconstructor agent

**Files:**
- Create: `.claude/agents/reconstructor.md`

- [ ] **Step 1: Write the reconstructor agent**

Write `.claude/agents/reconstructor.md` with this content:

```markdown
---
name: reconstructor
description: Takes a Sanskrit folio with … lacunae, a classification block, and corpus search hits, then proposes Sanskrit reconstructions for each gap with confidence labels. Runs validation searches on uncertain proposals. Returns a reconstructed folio and per-lacuna notes.
tools: Bash, Read, Write, Glob, Grep
---

You receive three inputs:

1. **FOLIO** — the raw Sanskrit folio text with `…` lacunae
2. **CLASSIFICATION** — the structured block from the classifier agent
3. **CORPUS HITS** — trimmed results from the corpus-searcher agent

Your job is to propose Sanskrit text for each `…` and produce a reconstructed folio plus lacuna notes. You do not translate.

## Confidence labels

- `◆ Attested` — the gap is directly filled by a parallel passage in the corpus hits
- `◇ Probable` — a corpus hit overlaps with surrounding text and the reconstruction follows closely from it plus grammatical/metrical constraints
- `○ Speculative` — no relevant corpus hit; reconstruction based on context, school vocabulary, and genre conventions only

## Per-lacuna process

For each `…` in order:

1. **Read context** — examine the surviving Sanskrit immediately before and after the gap. Note:
   - Grammatical constraint: what case, number, gender, verb form is expected?
   - Metrical constraint: if verse, how many syllables are missing and what prosodic shape is needed?
   - Thematic constraint: what does the argument require at this point?

2. **Check corpus hits** — scan the CORPUS HITS for any passage whose surrounding text matches the folio's surviving text. If found, extract the corresponding portion as a candidate reading. List multiple candidates if present.

3. **Propose reconstruction** — if a parallel covers the gap, use it (label `◆` or `◇`). If not, generate Sanskrit that fits the grammatical, metrical, and thematic constraints using your knowledge of the identified school's vocabulary (label `○`).

4. **Validate uncertain proposals** — for `◇` and `○` proposals, run a validation search:

```bash
echo '{
  "search_input": "<your proposed Sanskrit phrase>",
  "search_type": "regular",
  "filter_source_language": "sa",
  "max_depth": 30,
  "do_ranking": false
}' | ./scripts/primary-search.sh --trim
```

If this returns a hit that supports your reconstruction, upgrade the label (○ → ◇, or ◇ → ◆ if the match is exact).

## Output format

Return two sections:

### RECONSTRUCTED FOLIO

The full folio text with reconstructed portions marked with ⟨angle brackets⟩ and their confidence label inline:

```
yat sat tat ⟨kṣaṇikam⟩ [◇] arthakriyāsamartham |
...
```

### LACUNA NOTES

One entry per gap:

```
Lacuna 1
  Position: after "yat sat tat"
  Estimated akṣaras: 3–5
  Syntactic slot: predicate adjective qualifying sat
  Candidates:
    - ⟨kṣaṇikam⟩ — from corpus hit: Pramāṇavārttika 2.3 (SA_xxx); surrounding text matches
    - ⟨anityam⟩ — generated; fits metrically and grammatically
  Chosen: ⟨kṣaṇikam⟩ [◇ Probable]
  Rationale: corpus hit SA_xxx has "yat sat tat kṣaṇikam" in nearly identical context; Dharmakīrti's standard formulation.
  Validation search: "yat sat tat kṣaṇikam" → 2 hits found; label upgraded.
```
```

- [ ] **Step 2: Verify the file exists and has correct frontmatter**

```bash
head -5 .claude/agents/reconstructor.md
```

Expected:
```
---
name: reconstructor
description: Takes a Sanskrit folio with … lacunae, a classification block, and
```

- [ ] **Step 3: Commit**

```bash
git add .claude/agents/reconstructor.md
git commit -m "Add reconstructor subagent for folio reconstruction"
```

---

### Task 4: Create the /reconstruct command

**Files:**
- Create: `.claude/commands/reconstruct.md`

- [ ] **Step 1: Write the command file**

Write `.claude/commands/reconstruct.md` with this content:

```markdown
---
description: Analyse a Sanskrit folio with … lacunae — classify the text, search the canonical corpus for parallels, reconstruct the missing Sanskrit, and translate the whole. Writes a philological report to output/reconstructions/.
argument-hint: <path under sources/>
---

User's request: $ARGUMENTS

## Step 1: Read the input folio

Read the file at `$ARGUMENTS`. If it is not found, check `sources/$ARGUMENTS`. Report the filename and line count to the user before proceeding.

## Step 2: Dispatch parallel agents

Launch the **classifier** agent and the **corpus-searcher** agent at the same time — do not wait for one before starting the other.

**Classifier agent prompt:**
> Analyse this Sanskrit folio and produce a classification block per your instructions.
> FOLIO:
> [paste full folio text]

**Corpus-searcher agent prompt:**
> Search the Buddhist canonical corpus for passages parallel to this Sanskrit philosophical folio. Run three searches:
> 1. Semantic search on the longest coherent surviving fragment (filter_source_language: "sa" first, then "all" if results are sparse).
> 2. Regular (lexical) search on each of the distinctive technical terms visible in the folio, one call per term (filter_source_language: "sa").
> 3. Cross-language semantic search with filter_source_language: "all" and filter_target_language: "all".
> Keep only hits whose summary indicates genuine parallel content. Group results by source/title. Preserve src_link verbatim on every hit.
> FOLIO:
> [paste full folio text]

Wait for both agents to return before proceeding.

## Step 3: Reconstruct lacunae

Dispatch the **reconstructor** agent with all three inputs:

> Reconstruct the lacunae in this Sanskrit folio. Here are your three inputs:
>
> FOLIO:
> [paste full folio text]
>
> CLASSIFICATION:
> [paste classifier output]
>
> CORPUS HITS:
> [paste corpus-searcher output]

Wait for the reconstructor to return.

## Step 4: Translate

POST to cat-translate using `./scripts/cat-translate.sh`. Build the JSON body from the reconstructed folio (use the RECONSTRUCTED FOLIO section from the reconstructor output — ⟨angle brackets⟩ and confidence labels included):

```bash
echo '{
  "input_sanskrit": "<reconstructed folio — one line per sentence, \\n-separated, ⟨reconstructed portions⟩ preserved>",
  "context": "<classification block — school, opponent, topic in one short paragraph>",
  "focus": "equal",
  "target_language": "english",
  "style_instruction": "academic register, IAST for Sanskrit technical terms on first occurrence with English gloss in parentheses, render text inside ⟨angle brackets⟩ in [square brackets] in the translation to mark reconstructed portions, scholarly prose matching modern Buddhist epistemology studies"
}' | ./scripts/cat-translate.sh
```

## Step 5: Write the report

Create `output/reconstructions/` if it does not exist. Write the report to `output/reconstructions/<basename-of-input-file>.md` with this structure:

```
# Folio Reconstruction: <filename>

## 1. Classification
<paste classifier output, reformatted as readable prose>

## 2. Corpus Parallels
<paste corpus-searcher output — one block per hit with title, segmentnr, excerpt, src_link>

## 3. Reconstructed Folio
<paste RECONSTRUCTED FOLIO section from reconstructor — attested text in roman, ⟨reconstructed⟩ with confidence label>

## 4. Translation
<paste cat-translate response — reconstructed portions in [square brackets]>

## 5. Lacuna Notes
<paste LACUNA NOTES section from reconstructor>
```

## Step 6: Report to user

Tell the user:
- Path of the report file written
- Number of lacunae processed
- Count by confidence label (◆ / ◇ / ○)
- Any unresolved difficulties (e.g. lacunae where no parallel was found and the reconstruction is uncertain)
```

- [ ] **Step 2: Verify the file exists and has correct frontmatter**

```bash
head -5 .claude/commands/reconstruct.md
```

Expected:
```
---
description: Analyse a Sanskrit folio with … lacunae — classify the text, search
```

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/reconstruct.md
git commit -m "Add /reconstruct slash command for folio reconstruction workflow"
```

---

### Task 5: Smoke test

**Files:**
- Read: `sources/test-folio.txt` (created in Task 1)
- Verify: `output/reconstructions/test-folio.txt.md` is created with all 5 sections

- [ ] **Step 1: Run the command**

In the Claude Code session, run:

```
/reconstruct sources/test-folio.txt
```

- [ ] **Step 2: Verify the output file exists**

```bash
ls output/reconstructions/test-folio.txt.md
```

Expected: file exists (non-zero size).

- [ ] **Step 3: Verify all five sections are present**

```bash
grep "^## " output/reconstructions/test-folio.txt.md
```

Expected output (order matters):
```
## 1. Classification
## 2. Corpus Parallels
## 3. Reconstructed Folio
## 4. Translation
## 5. Lacuna Notes
```

- [ ] **Step 4: Verify confidence labels are present**

```bash
grep -c "◆\|◇\|○" output/reconstructions/test-folio.txt.md
```

Expected: a number > 0 (at least one lacuna has a label).

- [ ] **Step 5: Verify src_link format on corpus hits**

```bash
grep "dharmamitra.org" output/reconstructions/test-folio.txt.md | head -3
```

Expected: one or more lines containing `https://dharmamitra.org/nexus/...` URLs (verbatim from the API — not constructed).

If this returns nothing the corpus search found no parallels for the test folio, which is acceptable — the workflow still passes as long as the sections exist and lacunae have `○ Speculative` labels.

- [ ] **Step 6: Commit**

```bash
git add output/reconstructions/test-folio.txt.md
git commit -m "Add smoke test output for /reconstruct command"
```

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|---|---|
| `/reconstruct <path>` slash command | Task 4 |
| Classification agent (school, opponent, topic, register, terms, lacuna inventory) | Task 2 |
| Corpus search — 3 passes (semantic on text, regular on terms, cross-language) | Task 4 (corpus-searcher prompt) |
| Parallel dispatch of classifier + corpus-searcher | Task 4 Step 2 |
| Reconstruction with ◆/◇/○ confidence labels | Task 3 |
| Validation search for ◇/○ proposals | Task 3 |
| cat-translate with ⟨⟩ → [] convention | Task 4 Step 4 |
| Output report with 5 sections | Task 4 Step 5 |
| `output/reconstructions/` output directory | Task 1 + Task 4 |
| Smoke test | Task 5 |

All spec requirements covered. No TBDs or placeholders. Agent names consistent throughout (classifier, reconstructor, corpus-searcher). Confidence label symbols (◆ ◇ ○) consistent across Tasks 3, 4, and 5.
