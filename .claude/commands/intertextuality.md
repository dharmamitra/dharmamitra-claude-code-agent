---
description: Map how a text relates to the rest of the canon — which works quote / share / rework it, where its passages travel across collections and languages. Drives DharmaNexus's matches / table-view layer and writes an intertextuality report to output/intertextuality/.
argument-hint: <text title / author / description, a filename, or a segmentnr>
---

Target: $ARGUMENTS

Drive an intertextuality workflow.

1. **Resolve identity.** If `$ARGUMENTS` is already a DharmaNexus `filename` (e.g. `SA_T07_vakobhau`)
   or a `segmentnr`, use it directly. Otherwise run `./scripts/identify-text.py "$ARGUMENTS" --top 5`
   to resolve the title/author/description to a `filename`, and confirm the match by its `displayName`
   (show the user the top candidates if it's ambiguous).

2. Delegate to the **intertextual-researcher** subagent. It will:
   - Survey the whole-text intersection with `./scripts/nexus.sh table <filename> --agg` (which texts
     share material, how much, how strongly), then drill into the significant target texts.
   - Trace specific passages outward with `./scripts/nexus.sh matches <segmentnr> …` when the question
     is about a single verse or sentence.
   - Use the rich filters (`--include-files` / `--include-categories` / `--include-collections` /
     `--languages`) for focused comparisons, and read `tgt_lang` to flag cross-language transmission.
   - Read `./scripts/nexus.sh menu <lang> --meta <filename>` for date estimates and known translations
     when interpreting direction of borrowing.
   - Write the report to `output/intertextuality/<work>.md`.

3. Report back: which text was identified, how many neighbouring texts it intersects, the most
   significant parallels, any cross-language transmission, and the file path written.

Caveat: a `table` call can return 0 rows even for a correctly-identified text whose overlaps were never
precomputed — that is not "no relationship". Fall back to the root/base text or to `matches`/`/primary/`
on its segments, and say which path produced the result.
