# output/

Everything Claude writes lands here.

```
output/
  translations/
    <work>.brief.md      # translation brief: target lang, style, terminology
    <work>.chunks.md     # the chunking plan
    <work>.md            # the running translation, appended chunk by chunk
  critical-editions/
    <work>.md            # the apparatus: anchor, parallels, variants, emendations
    <work>.brief.md      # philology brief if relevant
```

The translator and philologist agents write incrementally — they do **not**
rewrite these files from scratch on every iteration. Safe to keep them open in
an editor and read along during a long run.

You can also hand-edit any of these files between runs. The agents will
re-read them before continuing.
