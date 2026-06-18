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
