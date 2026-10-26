---
name: turn-into-rag
description: Distills books, papers, web articles, videos and audio (PDF, Word, EPUB, HTML, web pages, YouTube, mp4, mp3) into citation-tracked Markdown knowledge files built for RAG retrieval. Use when the user wants a source turned into reference knowledge or a knowledge base, or asks the agent to read, study or learn a book, paper, page or video so it can be consulted later.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Turn into RAG

**Distill** one source into Markdown files an agent can retrieve from later. Distill, don't summarize: a summary keeps the gist and loses the specifics. Distillation drops the filler and keeps every specific (numbers with units, procedures, thresholds, names), each tied to its **locator** so any claim can be traced back to the source.

Three terms run the process:

- **Ledger**: `ledger.md`, one row per section of the source. The source is done when every row reads `done` or `skipped — <reason>`.
- **Locator**: where a claim lives in the source (`p. 92`, `[00:12:34]`). Every specific carries one.
- **Orphan test**: any H2 section, pulled alone into a prompt with nothing around it, still says what it is about and stays true. RAG retrieves sections, not files, so a section that fails is a broken chunk.

`<skill-dir>` below is the folder holding this file.

## Output

The knowledge base is `knowledge/` at the workspace root, unless the repo already keeps one (use it) or the user names another place.

```
knowledge/
├── INDEX.md               one line per source; the entry point for retrieval
├── <slug>.md              short source (1 ledger row): a single file
└── <slug>/                long source (2+ rows)
    ├── 00-overview.md     source card, key takeaways, map of the files
    ├── 01-<topic>.md …    one file per ledger row
    ├── glossary.md
    ├── ledger.md          kept as the record of what was covered and skipped
    └── _raw/              staging, deleted at the end
```

Markdown is the source of truth. Agents can grep and read it directly, and every RAG splitter chunks on its headings and lifts its frontmatter as metadata. JSONL for a vector store is generated from it on demand (see Export). Templates for every file are in [FORMAT.md](FORMAT.md).

## Step 0 — Bootstrap

On a new machine the libraries are usually missing, so check before staging anything: `python <skill-dir>/scripts/stage.py --check` lists each one as `OK` or `MISSING`. Install whatever the source needs, from the requirements files:

| Source | Python libraries | Install |
|---|---|---|
| PDF | pymupdf, pymupdf4llm | `pip install -r <skill-dir>/scripts/requirements.txt` |
| DOCX, PPTX, XLSX, EPUB | markitdown | (same file) |
| Web pages, HTML | trafilatura | (same file) |
| Chunk export | pyyaml | (same file) |
| Video URLs (YouTube…) | yt-dlp | `pip install -r <skill-dir>/scripts/requirements-media.txt` |
| Audio and video transcription | faster-whisper, av, numpy | (same file) |
| Video frames | av, pillow | (same file) |

Needs Python 3.10 or newer. Whisper downloads its model on first use (`small` ≈ 460 MB). Optional system tools, only for the cases in SOURCES.md: Tesseract + ocrmypdf (scanned PDFs), LibreOffice (legacy .doc/.ppt). No ffmpeg is needed.

**Done when** `--check` shows `OK` for every library this source needs.

## Step 1 — Stage

To resume: if `knowledge/<slug>/ledger.md` already exists with `todo` rows, skip to Step 2 at the first `todo` row.

```
python <skill-dir>/scripts/stage.py "<path-or-url>" --kb knowledge --slug <slug> [--title "<title>"] [--lang <code>] [--frames 30]
```

- `--slug`: a short kebab-case name taken from the real title (`industrial-cannabis-cultivation`). Also pass `--title` when the metadata title is junk. PDFs often carry titles like "Microsoft Word - final3".
- `--frames N`: for a local video whose picture carries information (demos, slides, gauges, setups). It keeps a deduplicated frame every N seconds.
- Transcription on CPU can take as long as the media itself. For media longer than about 10 minutes, run the command in the background and wait for it.

The script converts the source to text with locator markers (`[[p. 12]]` at page changes, `[00:12:34]` on transcript paragraphs). It splits the text along the source's own TOC or headings into rows of at most 9,000 words, then writes `ledger.md` plus one raw file per row in `_raw/sections/`.

**Done when** the script prints `"ok": true`, the first raw section reads cleanly (no garbled characters, no words run together), and every warning it printed is resolved via [SOURCES.md](SOURCES.md). If the script fails, or the source is something it can't take (cloud links, DRM ebooks, images), SOURCES.md gives the route.

## Step 2 — Distill, row by row

For each `todo` row, in ledger order:

1. Read the row's whole raw file, every paragraph, without skimming. View every frame or page image it lists, and follow its `NOTE:` lines.
2. Write its distilled file following the Distillation rules below and FORMAT.md. Name it for the topics it covers (`04-lighting.md`, not `04-part-2.md`).
3. Add the new terms to `glossary.md`.
4. Update the row with the distilled word count and status `done`. A row with nothing worth keeping (copyright page, index, bibliography, ads) gets `skipped — <reason>` and no file.

Write each file before you open the next raw section. The files on disk hold the progress, so a context reset costs at most one row.

Check the distilled-to-raw word ratio as you tick each row. Narrative or conversational text usually lands at 5–15%, technical text at 15–35%, and dense reference text (specs, formulas, tables) can run higher. Under 5% usually means skimming: re-read the raw file and recover what was lost before ticking the row.

If the platform offers subagents and the ledger is long, give out one row per subagent. Tell each to read this file's Distillation rules and FORMAT.md. The main agent still opens every returned file and updates the ledger itself.

**Done when** every row is `done` or `skipped — <reason>`, and every `done` row is at 5% or above or has been re-checked.

## Step 3 — Assemble

1. Write `00-overview.md` now, when the whole source is known: the source card, 10–20 key takeaways (each pointing to the file that holds it), and a map of every file.
2. Deduplicate and alphabetize `glossary.md`.
3. Add or update the source's line in `knowledge/INDEX.md`.

For a single-file source, the card, takeaways, distilled sections and glossary all go in `knowledge/<slug>.md` (layout in FORMAT.md).

**Done when** the overview links every distilled file and INDEX.md has the source's line.

## Step 4 — Verify and clean up

1. **Fact check.** Pick 10 specific claims spread across the files, numbers first. Find each one in `_raw/source.md` by its locator and compare. If any claim doesn't match, fix it and re-check every claim in that file.
2. **Orphan test** five random H2 sections. Rewrite any that depend on a neighbour ("as above", "this method", a bare heading like "Results").
3. Delete `knowledge/<slug>/_raw/` unless the user asked to keep it, because the raw text of a whole book doesn't belong in git. For a single-file source, delete the whole `knowledge/<slug>/` folder.
4. Report the files written, rows skipped and why, any warnings left open, and the INDEX line.

**Done when** all 10 claims match the raw text, `_raw/` is gone or kept by request, and the report is delivered.

## Export (only when asked for vector-store ingestion)

`python <skill-dir>/scripts/export_chunks.py knowledge` writes `knowledge/chunks.jsonl`: one chunk per H2 section, with its breadcrumb (`title › heading`) and the file's frontmatter as metadata. Regenerate it after any edit.

## Distillation rules

**Keep** exact values and units, never rounded:

- Numbers: quantities, ranges, doses, rates, durations, temperatures, costs and yields, with the conditions they hold under.
- Procedures: steps in order, with the quantities and timings inside them.
- Decision rules and thresholds: if X then Y, limits, when to do what.
- Definitions and classifications.
- Mechanisms: the *why* behind a recommendation.
- Problems: symptoms → causes → fixes, plus warnings and failure modes.
- Comparisons and trade-offs. Tables stay tables.
- Formulas, with each variable's meaning and unit.
- Named things: species and cultivars, equipment, products, standards, regulations, and studies (with design, sample size and key result).
- The author's recommendations and opinions, attributed as such ("the author recommends…").

**Drop:** anecdotes (keep the lesson if it carries a fact), repeated statements (keep the most complete one, once), marketing, motivational filler, chapter intros and recaps, acknowledgements, indexes.

**Fidelity:**

- Nothing goes in the files that the source doesn't say. Your own additions (a unit conversion, a contradiction between chapters, a claim that looks outdated) go on a `> Note:` line.
- Keep the source's terms. If the book says EC, every file says EC.
- Write in the source's language unless the user asks otherwise. When translating, give each technical term in the original language in parentheses on first use.
- When the source contradicts itself, keep both versions, each with its locator, and add a Note.

**Weight by source type:**

| Source | Weight toward |
|---|---|
| Book, manual, SOP | procedures, parameters, decision rules, troubleshooting |
| Paper | question, method (design, n, conditions), results with effect sizes and statistics, limitations |
| Web article | the specific claims; author, site and date, because web advice ages fast |
| Lecture, tutorial video | steps both shown and spoken; what the frames show (setups, readings, slides) |
| Podcast, interview | claims attributed to the speaker by name; skip the banter |
| Regulation, standard | requirements near-verbatim with article numbers; obligations, deadlines, scope |
