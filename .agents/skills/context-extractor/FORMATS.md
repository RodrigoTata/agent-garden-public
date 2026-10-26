# Format-Specific Extraction Rules

Reference for how `extract.py` handles each supported format. Consult when troubleshooting extraction quality or adding support for a new format.

---

## PDF (`.pdf`)

**Library**: `pymupdf4llm` (markdown-native extraction via PyMuPDF)

- Extracts text as markdown preserving headings, bold, italic, lists, and tables.
- Each page becomes a chunk boundary candidate. Pages shorter than 20 lines merge with the next page.
- Embedded images are noted as `[Image on page N]` placeholders — not extracted.
- Scanned PDFs (image-only) produce empty text. The script warns: `"⚠ PDF appears to be scanned/image-only. No text extracted."`.

---

## Excel (`.xlsx`, `.xls`)

**Library**: `openpyxl`

- Each **sheet** becomes a separate section with heading `## Sheet: <name>`.
- Data is rendered as a markdown table. Header row is the first non-empty row.
- Merged cells repeat the value across the merged range.
- Sheets with fewer than 2 rows of data are skipped with a note.
- Formulas are resolved to their **computed values** when available; otherwise the formula text is kept.
- Maximum 200 columns per sheet. Columns beyond that are truncated with a warning.

---

## Word (`.docx`)

**Library**: `python-docx`

- Paragraphs preserve their heading level (`Heading 1` → `#`, `Heading 2` → `##`, etc.).
- Tables are rendered as markdown tables.
- Bold, italic, and underline inline styles are preserved.
- Images are noted as `[Embedded image]` placeholders.
- Headers/footers are extracted as a separate section at the top.

---

## PowerPoint (`.pptx`)

**Library**: `python-pptx`

- Each **slide** becomes a section: `## Slide N: <title>`.
- Text from all shapes (text boxes, titles, content placeholders) is extracted.
- Tables within slides are rendered as markdown tables.
- Speaker notes are included under a `> Notes:` blockquote per slide.
- Images are noted as `[Image: <filename>]` placeholders.

---

## CSV / TSV (`.csv`, `.tsv`)

**Library**: Python stdlib `csv`

- Rendered as a single markdown table.
- First row is treated as header.
- Files larger than 500 rows are chunked into sections of 200 rows each, with the header repeated.
- Delimiter is auto-detected (comma, semicolon, tab).

---

## Plain Text / Markdown (`.txt`, `.md`, `.log`)

- Read verbatim.
- Chunked at paragraph boundaries (double newline) when the file exceeds 300 lines.
- Markdown files preserve all formatting.

---

## Chunking Strategy

All formats follow the same post-extraction chunking:

1. **Structural boundaries first**: Split at heading changes (H1, H2), sheet/slide transitions, or page breaks.
2. **Size cap**: No chunk exceeds ~400 lines. Oversized sections split at the nearest paragraph boundary.
3. **Context overlap**: Each chunk includes the last 3 lines of the previous chunk as overlap, prefixed with `<!-- context -->`, to preserve continuity during retrieval.
4. **Metadata header**: Every chunk starts with a YAML frontmatter block:

```yaml
---
source: "path/to/original.xlsx"
chunk: 3
total_chunks: 12
section: "Sheet: Cronograma"
extracted_at: "2026-08-30T10:25:00"
---
```
