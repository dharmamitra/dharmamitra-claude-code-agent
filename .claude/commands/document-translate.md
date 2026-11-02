---
description: Scholarly translation of a whole document (Tibetan, Sanskrit or Chinese) by the session's own model, with document context carried between chunks, a growing project glossary, analysis before rendering, 3 + 3 research calls per chunk, completeness checks, independent review and uncertainty markers.
argument-hint: <path under sources/> [references/<work>/]
---

User's request: $ARGUMENTS

Run the document-translation recipe: the agent running this session translates, chunk by chunk,
with document context, and DharmaMitra's public APIs are its research tools.

1. Resolve the source as in `/translate` (a path, pasted text, or a work name under `sources/`).
   Determine the source language and the work name.

2. Look for project inputs in `references/<work>/`, or in `references/` if there is no work
   folder: `glossary.md`, `conventions.md`, `prior-translations/`, `commentaries/`, an outline.
   Binary files (.docx, .pdf) go to the **reference-reader** subagent first.

3. Delegate to the **document-translator** subagent. It sets up `output/documents/<work>/`
   (glossary, conventions, `work/` files) and translates chunk by chunk, following
   `.claude/agents/document-translator.md`. It checkpoints every 10 chunks.

4. When the run finishes or pauses, summarise: chunks done / total, the files written, new
   glossary terms, and the chunks with the lowest confidence that a human should read first
   (from `summary.md`).

For a single paragraph without document context, `/research-translate` is the lighter recipe.
