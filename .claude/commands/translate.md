---
description: Translate a source passage or file (Sanskrit / Tibetan / Pali / Chinese) using DharmaMitra's cat-translate API, threading in any reference glossaries the user has under references/.
argument-hint: <path under sources/ or pasted text>
---

User's request: $ARGUMENTS

Drive a translation workflow against DharmaMitra's cat-translate API.

1. If `$ARGUMENTS` is a path, read it. If it's text, treat it as the source. If it looks like a work name with no extension (e.g. "Vajracchedikā"), search `sources/` for matching files in all four canon-language conventions (`<name>.bo.txt`, `<name>.sa.txt`, `<name>.zh.txt`, `<name>.pa.txt`).

2. Delegate to the **reference-reader** subagent first to scan `references/` and produce `output/translations/<work>.brief.md`. If a brief already exists, the subagent should merge findings into it.

3. Delegate to the **translator** subagent to chunk (3–5 sentences per chunk), iterate through `cat-translate`, and write `output/translations/<work>.md` incrementally. Have it checkpoint every 5 chunks so the user can adjust terminology before drift sets in.

4. When the run finishes (or pauses for checkpoint), summarise: chunks done / total, file written, any unresolved terminology questions.

Defaults: `focus: "equal"`, `target_language: "english"`, `max-time: 90s` on the curl call (already set in the script). Do not lower these without an explicit user instruction.
