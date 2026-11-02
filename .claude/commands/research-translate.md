---
description: Translate a Tibetan, Sanskrit or Chinese passage or file yourself (the session's own model), researching each paragraph with DharmaMitra's parallel-passage search and the MITRA dictionary (3 + 3 calls per paragraph).
argument-hint: <path under sources/ or pasted text> [--engine gemini]
---

User's request: $ARGUMENTS

First, show the user the Gemini notice from `.claude/agents/research-translator.md` (Gemini 3.8 Flash gives better results;
set `GEMINI_API_KEY` and add `--engine gemini`). If `--engine gemini` was given but `GEMINI_API_KEY` is not set,
say so and ask whether to continue with the session's own model.

Run the research-translation recipe: the agent running this session translates, and DharmaMitra's
public APIs are its research tools.

1. If `$ARGUMENTS` is a path, read it. If it is text, treat it as the source. If it looks like a work
   name without an extension, search `sources/` for `<name>.bo.txt`, `<name>.sa.txt`, `<name>.zh.txt`,
   `<name>.pa.txt`. Determine the source language (`bo`, `sa`, `zh`, `pa`). If there are several
   witnesses, translate the one the user names, or ask.

2. If `references/` has glossaries or prior translations and no brief exists yet, delegate to the
   **reference-reader** subagent to write `output/translations/<work>.brief.md` first.

3. Delegate to the **research-translator** subagent. It chunks into paragraphs, researches each one with
   `./scripts/research.py` (at most 3 `search` calls and 3 `dict` calls per paragraph, separate budgets),
   translates it, and appends to `output/translations/<work>.research.md`, checkpointing every
   10 paragraphs.

4. When the run finishes or pauses, summarise: paragraphs done / total, file written, open
   terminology questions.

For a single short passage (one paragraph), you may run the recipe directly instead of delegating:
same tools, same budgets, same output format.
