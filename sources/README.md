# sources/

Drop the source texts you want to work with in here.

## Conventions the translator agent expects

For multi-witness work, name files by language code:

```
sources/
  vajracchedika.sa.txt    # Sanskrit (Devanagari or IAST)
  vajracchedika.bo.txt    # Tibetan (Unicode or Wylie)
  vajracchedika.zh.txt    # Classical Chinese
  vajracchedika.pa.txt    # Pali (Roman / IAST)
```

The work stem (`vajracchedika`) is used as the output filename
(`output/translations/vajracchedika.md`). Use lowercase, no spaces.

For single-witness work, one file is enough — same naming pattern.

You can also paste source text directly into the chat. The translator and
philologist agents handle both.

## Formats

- `.txt` — plain UTF-8.
- `.md` — Markdown is fine; structural headers help with chunking.
- `.docx`, `.pdf`, `.epub` — use the **reference-reader** agent to extract first.
  Don't paste binary files into the chat.
