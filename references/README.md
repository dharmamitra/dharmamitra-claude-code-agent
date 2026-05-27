# references/

Drop reference materials in here. The **reference-reader** subagent will scan
this folder at the start of a translation or philology session and digest the
contents into a `*.brief.md` file that the translator agent threads through
every API call.

## What goes here

- **Glossaries** — your preferred renderings of technical terms. Plain text or Markdown tables work best.
- **Prior translations** — published or draft translations of the same work, or of related works using the same terminology. Used to sample style and named-entity forms.
- **Style guides / editorial notes** — explicit instructions about how to render things. One sentence of "use Latinate vocabulary, no contractions, preserve Skt. technical terms" is worth more than 100 pages of academic prose.
- **Critical editions** — variant readings, sigla, apparatus. Used by the philologist agent.
- **Secondary literature** — academic articles. Useful for context; less useful for terminology unless the author explicitly defends a translation choice.

## Formats

| Extension | Handling |
| --- | --- |
| `.txt`, `.md` | read directly |
| `.docx` | converted via `pandoc` (or `textutil` on macOS) |
| `.pdf` | converted via `pdftotext` (poppler) |
| `.epub`, `.html` | converted via `pandoc` |

If a conversion tool isn't installed, the agent will tell you. On macOS:

```bash
brew install pandoc poppler
```

## Subdirectories are fine

Organise however you like — the agent does a recursive scan. A useful pattern:

```
references/
  glossary.md
  style-guide.md
  prior-translations/
    bodhi-1995-majjhima-nikaya.txt
    conze-1958-vajracchedika.txt
  critical-editions/
    schmithausen-1987-alayavijnana-apparatus.pdf
```
