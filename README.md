# DharmaMitra Agent Starterpack

Download this folder, open it in Claude Code, and you have a working setup
for two things:

1. **Translating classical Asian Buddhist texts** (Tibetan, Chinese, Pali, Sanskrit → English / German / …) using DharmaMitra's multi-witness translation API, with your own reference glossaries and prior translations threaded in as context.
2. **Critical-edition / philological work** — using cross-language parallel retrieval to surface variant readings, propose emendations, and build a structured apparatus around a passage.

No DharmaMitra account or API key is required. The endpoints are public.

---

## Get started in 3 steps

### 1. Prerequisites

You need:

- **[Claude Code](https://claude.com/claude-code)** installed.
- `curl` (preinstalled everywhere).
- `jq` (for trimming search responses): `brew install jq` or `apt install jq`.
- *Optional, for reading PDF/DOCX/EPUB references:*
  - `pandoc` (`brew install pandoc`)
  - `pdftotext` (`brew install poppler` or `apt install poppler-utils`)

### 2. Download / clone

```bash
git clone <this-repo-url> dharmamitra-agent
cd dharmamitra-agent
```

### 3. Verify the endpoints are reachable

```bash
./scripts/cat-translate.sh --file examples/cat-translate-sutra-opening.json --pretty
./scripts/primary-search.sh --file examples/primary-search-semantic.json --trim
```

The first should return a JSON object with a `translation` field; the second
should return a `results` array. If either errors, see **Troubleshooting** below.

### 4. Open in Claude Code

```bash
claude
```

Claude Code will read `CLAUDE.md` and `.claude/agents/*` automatically. Try:

```
/translate sources/your-text.sa.txt
/find-parallels evaṃ mayā śrutam
/critical-edition sources/your-passage.txt
```

---

## What's in this folder

```
.
├── CLAUDE.md                    # project context — read first by Claude
├── README.md                    # this file
├── .claude/
│   ├── settings.json            # allowlists the scripts so you don't get permission prompts
│   ├── agents/                  # specialised subagents
│   │   ├── translator.md        # iterative multi-witness translation
│   │   ├── philologist.md       # critical apparatus, variants, emendations
│   │   ├── corpus-searcher.md   # focused /primary/ search
│   │   └── reference-reader.md  # digests references/ into a translation brief
│   └── commands/                # slash commands
│       ├── translate.md
│       ├── find-parallels.md
│       ├── critical-edition.md
│       └── lookup-segment.md
├── scripts/
│   ├── cat-translate.sh         # POST /cat-translate/v1/translate
│   ├── primary-search.sh        # POST /primary/
│   └── trim-primary.sh          # strip vector + text_new from search responses
├── sources/                     # ← drop your source texts here
├── references/                  # ← drop your reference materials here
├── output/                      # ← Claude writes translations + apparatus here
└── examples/                    # ready-to-run request bodies
```

---

## Typical workflows

### Translating a sūtra — the "translator mill"

The headline workflow is a translator mill: Claude works page by page through
a long document, and each API call carries forward the translation it just
produced on the previous chunk. That's how a 300-page translation stays
internally consistent — the running translation feeds back into each next
call's `context` field, alongside any prior translation of the same work that
*you* have already produced.

1. Put your source text under `sources/`. Use language suffixes if you have multiple witnesses:

   ```
   sources/vajracchedika.sa.txt
   sources/vajracchedika.bo.txt
   ```

2. Drop any glossaries, style guides, or **prior translations of this work** under `references/`. Plain text, Markdown, DOCX, and PDF all work. If you've already translated chapters 1–3 and want to continue with chapter 4, drop your existing translation in too — Claude will weave it into the `context` for every call.

3. Tell Claude:

   ```
   /translate sources/vajracchedika
   ```

   Claude will:
   - Scan `references/` and write `output/translations/vajracchedika.brief.md` with your terminology choices and style.
   - Chunk the source into ~3–5 sentence units (the API's sweet spot).
   - Call `cat-translate` iteratively. Each call's `context` is built fresh: the last ~1–2 pages of translated prose, any matching reference translation, and the relevant glossary lines.
   - Write to `output/translations/vajracchedika.md` incrementally.
   - Pause every 5 chunks to let you adjust terminology. Corrections you make to the brief are picked up automatically on the next chunk.

### Building a critical apparatus

1. Put the anchor passage in `sources/`, or paste it inline.

2. Tell Claude:

   ```
   /critical-edition sources/passage.sa.txt
   ```

   Claude will:
   - Retrieve parallels via `/primary/` (semantic search, all languages, max_depth 30).
   - Triage hits: canonical text vs. commentary citation vs. parallel passage.
   - Compare witnesses against the anchor — flag variant readings, lacunae, pluses.
   - Propose emendations where one witness's reading clearly fits better, citing the parallels that support it.
   - Drill into suspect words with targeted follow-up searches.
   - Write the apparatus to `output/critical-editions/<work>.md` with `src_link`s back to the DharmaMitra reading room for every citation.

### Finding parallels for a passage you know

```
/find-parallels the nature of mind is clear light
```

Returns a numbered list of hits — title, segmentnr, language, excerpt, deep-link.
For exact-phrase searches (proper names, distinctive phrasings), the agent will
pick `regular` search automatically.

### Pulling one passage by ID

```
/lookup-segment BO_K01_D0006:42b-3
```

Direct lookup via `source_filters.segmentnr`.

---

## How the API endpoints work

This kit wraps two DharmaMitra endpoints. Full reference is in `CLAUDE.md`; quick summary:

| Endpoint | What it does | Wrapper | Latency |
| --- | --- | --- | --- |
| `POST /cat-translate/v1/translate` | Synthesises one translation from up to 4 canon-language witnesses, with your own context/glossary mixed in | `./scripts/cat-translate.sh` | 3–8 s |
| `POST /primary/` | Searches Kangyur/Tengyur/Taishō/Nikāyas/Skt. critical eds. by meaning or exact text | `./scripts/primary-search.sh` | 0.3–3 s |

Both are public (no auth), JSON in / JSON out, synchronous. The scripts pipe a
JSON body in on stdin or take `--file body.json`. Add `--pretty` to
`cat-translate.sh` for human-readable output; add `--trim` to
`primary-search.sh` to strip the heavy `vector` field before reading results.

### Rate limits

- **cat-translate**: 200/min per IP, 8 000/day per IP. Generous for normal use.
- **/primary/**: **400/day per IP** (and 500/day per /24 subnet). This is the real practical ceiling — Claude's agents are configured to use `max_depth: 30` and budget follow-up searches accordingly. If you blow through 400/day, the next request returns 429.

---

## Customising

- **Style for translations**: edit `output/translations/<work>.brief.md` between runs. The translator agent re-reads it on the next chunk.
- **Allowed commands**: edit `.claude/settings.json`.
- **Agents**: edit `.claude/agents/*.md` — they're just Markdown files with YAML frontmatter. Change the workflow, tool scope, or default parameters to suit your project.
- **Slash commands**: edit `.claude/commands/*.md` — same format.

---

## Troubleshooting

**Curl returns 524 / "upstream timeout"** — the cat-translate call took >100 s. The Cloudflare upstream caps there. Cause is usually a very long input. Chunk smaller.

**`/primary/` returns 429** — you've hit the 400/day per-IP quota. Wait until tomorrow or use a different IP. The agents budget searches to avoid this; if you're hitting it from agent use, look at `output/` to see what's been happening.

**`/primary/` returns 0 results for an obvious query** — usually a script/filter mismatch. Try:
1. `filter_source_language: "all"` instead of `"auto"`.
2. `search_type: "semantic_only"` if your query script doesn't match the target corpus language.
3. Shorter, more distinctive query phrasing.

**`jq: command not found`** — install jq. `brew install jq` or `apt install jq`.

**The agent keeps drifting on terminology** — your brief is probably underspecified. Open `output/translations/<work>.brief.md`, write the rules you want enforced as the `style_instruction`, and tell the agent to restart the chunk where drift began.

---

## Citations

Every result from `/primary/` includes a `src_link` that deep-links into the
DharmaMitra reading room with the segment highlighted. Use those links verbatim
in your citations — don't construct DharmaMitra URLs yourself. The agents are
configured to do this automatically.
