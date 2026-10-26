#!/usr/bin/env python3
"""
context-extractor: extract.py
Digest binary documents into chunked markdown stored in .context-store/.

Usage:
  python extract.py <file_or_glob> [<file_or_glob> ...] --store <store_path>
  python extract.py --refresh --store <store_path>

Supported formats: PDF, XLSX/XLS, DOCX, PPTX, CSV/TSV, TXT, MD
"""

import argparse
import csv
import glob
import hashlib
import json
import os
import sys
import textwrap

# Fix Windows console encoding — avoid UnicodeEncodeError with emoji/unicode
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Format extractors — each returns a list of (section_title, text) tuples
# ---------------------------------------------------------------------------

def extract_pdf(filepath: str) -> list[tuple[str, str]]:
    import pymupdf4llm
    md = pymupdf4llm.to_markdown(filepath)
    if not md or not md.strip():
        print(f"⚠ PDF appears to be scanned/image-only. No text extracted: {filepath}", file=sys.stderr)
        return [("Document", "")]
    return [("Document", md)]


def extract_excel(filepath: str) -> list[tuple[str, str]]:
    from openpyxl import load_workbook
    wb = load_workbook(filepath, data_only=True, read_only=True)
    sections = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = []
        for row in ws.iter_rows(values_only=True):
            str_row = [str(c) if c is not None else "" for c in row]
            if any(cell.strip() for cell in str_row):
                # Truncate at 200 columns
                rows.append(str_row[:200])
        if len(rows) < 2:
            sections.append((f"Sheet: {sheet_name}", f"*Sheet has fewer than 2 data rows — skipped.*\n"))
            continue
        # Build markdown table
        header = rows[0]
        col_count = max(len(r) for r in rows)
        # Normalize row lengths
        for i, r in enumerate(rows):
            while len(r) < col_count:
                rows[i].append("")
        header = rows[0]
        separator = ["---"] * col_count
        lines = ["| " + " | ".join(header) + " |"]
        lines.append("| " + " | ".join(separator) + " |")
        for r in rows[1:]:
            lines.append("| " + " | ".join(r) + " |")
        if len(rows[0]) > 200:
            lines.append(f"\n*⚠ Columns truncated at 200 (original had {len(rows[0])}).*")
        sections.append((f"Sheet: {sheet_name}", "\n".join(lines)))
    wb.close()
    return sections


def extract_docx(filepath: str) -> list[tuple[str, str]]:
    from docx import Document
    doc = Document(filepath)
    lines = []
    for para in doc.paragraphs:
        style = para.style.name if para.style else ""
        text = para.text.strip()
        if not text:
            lines.append("")
            continue
        if "Heading 1" in style:
            lines.append(f"# {text}")
        elif "Heading 2" in style:
            lines.append(f"## {text}")
        elif "Heading 3" in style:
            lines.append(f"### {text}")
        elif "Heading" in style:
            lines.append(f"#### {text}")
        else:
            lines.append(text)
    # Extract tables
    for i, table in enumerate(doc.tables):
        lines.append(f"\n### Table {i + 1}\n")
        for j, row in enumerate(table.rows):
            cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            lines.append("| " + " | ".join(cells) + " |")
            if j == 0:
                lines.append("| " + " | ".join(["---"] * len(cells)) + " |")
    return [("Document", "\n".join(lines))]


def extract_pptx(filepath: str) -> list[tuple[str, str]]:
    from pptx import Presentation
    prs = Presentation(filepath)
    sections = []
    for i, slide in enumerate(prs.slides, 1):
        title = ""
        body_parts = []
        notes = ""
        for shape in slide.shapes:
            if shape.has_text_frame:
                text = shape.text_frame.text.strip()
                if shape == slide.shapes.title:
                    title = text
                elif text:
                    body_parts.append(text)
            if shape.has_table:
                table = shape.table
                rows = []
                for row in table.rows:
                    rows.append([cell.text.strip() for cell in row.cells])
                if rows:
                    header = rows[0]
                    tbl_lines = ["| " + " | ".join(header) + " |"]
                    tbl_lines.append("| " + " | ".join(["---"] * len(header)) + " |")
                    for r in rows[1:]:
                        tbl_lines.append("| " + " | ".join(r) + " |")
                    body_parts.append("\n".join(tbl_lines))
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame:
            notes_text = slide.notes_slide.notes_text_frame.text.strip()
            if notes_text:
                notes = f"\n> Notes: {notes_text}"
        section_title = f"Slide {i}: {title}" if title else f"Slide {i}"
        content = "\n\n".join(body_parts) + notes
        sections.append((section_title, content))
    return sections


def extract_csv(filepath: str, delimiter: str | None = None) -> list[tuple[str, str]]:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        sample = f.read(4096)
    if delimiter is None:
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
        except csv.Error:
            delimiter = ","
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = list(reader)
    if not rows:
        return [("CSV", "*Empty file.*")]
    header = rows[0]
    col_count = len(header)
    # Chunk large CSVs
    chunk_size = 200
    sections = []
    for start in range(1, len(rows), chunk_size):
        end = min(start + chunk_size, len(rows))
        chunk_rows = rows[start:end]
        lines = ["| " + " | ".join(header) + " |"]
        lines.append("| " + " | ".join(["---"] * col_count) + " |")
        for r in chunk_rows:
            # Normalize row length
            while len(r) < col_count:
                r.append("")
            lines.append("| " + " | ".join(r[:col_count]) + " |")
        label = f"Rows {start}-{end - 1}" if len(rows) > chunk_size + 1 else "Data"
        sections.append((label, "\n".join(lines)))
    return sections


def extract_text(filepath: str) -> list[tuple[str, str]]:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    return [("Document", text)]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

CHUNK_MAX_LINES = 400
OVERLAP_LINES = 3


def chunk_sections(sections: list[tuple[str, str]]) -> list[dict]:
    """Split extracted sections into sized chunks with metadata."""
    chunks = []
    for section_title, text in sections:
        lines = text.split("\n")
        if len(lines) <= CHUNK_MAX_LINES:
            chunks.append({"section": section_title, "content": text})
        else:
            # Split at paragraph boundaries (double newline)
            start = 0
            while start < len(lines):
                end = min(start + CHUNK_MAX_LINES, len(lines))
                # Try to find a paragraph boundary near the end
                if end < len(lines):
                    for probe in range(end, max(start + CHUNK_MAX_LINES // 2, start), -1):
                        if probe < len(lines) and lines[probe].strip() == "":
                            end = probe
                            break
                chunk_lines = lines[start:end]
                # Add overlap from previous chunk
                if start > 0 and start - OVERLAP_LINES >= 0:
                    overlap = lines[start - OVERLAP_LINES:start]
                    chunk_lines = [f"<!-- context --> {l}" for l in overlap] + chunk_lines
                chunks.append({"section": section_title, "content": "\n".join(chunk_lines)})
                start = end
    return chunks


# ---------------------------------------------------------------------------
# Store management
# ---------------------------------------------------------------------------

def load_index(store_path: str) -> dict:
    index_file = os.path.join(store_path, "index.json")
    if os.path.exists(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": 1, "documents": {}}


def save_index(store_path: str, index: dict):
    index_file = os.path.join(store_path, "index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)


def ingest_file(filepath: str, store_path: str) -> dict:
    """Ingest a single file into the store. Returns summary dict."""
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}", file=sys.stderr)
        return {"error": f"File not found: {filepath}"}

    ext = Path(filepath).suffix.lower()
    basename = Path(filepath).name

    # Detect format and extract
    extractors = {
        ".pdf": extract_pdf,
        ".xlsx": extract_excel,
        ".xls": extract_excel,
        ".docx": extract_docx,
        ".pptx": extract_pptx,
        ".csv": extract_csv,
        ".tsv": lambda p: extract_csv(p, delimiter="\t"),
        ".txt": extract_text,
        ".md": extract_text,
        ".log": extract_text,
    }

    if ext not in extractors:
        print(f"ERROR: Unsupported format '{ext}' for file: {filepath}", file=sys.stderr)
        return {"error": f"Unsupported format: {ext}"}

    print(f"[EXTRACT] {basename} ({ext})")
    sections = extractors[ext](filepath)

    # Chunk
    chunks = chunk_sections(sections)
    total_chunks = len(chunks)

    # Compute hash
    file_hash = sha256_file(filepath)
    digest_filename = f"{file_hash[:16]}.md"

    # Write digest file
    digests_dir = os.path.join(store_path, "digests")
    os.makedirs(digests_dir, exist_ok=True)
    digest_path = os.path.join(digests_dir, digest_filename)

    now = datetime.now(timezone.utc).isoformat()

    with open(digest_path, "w", encoding="utf-8") as f:
        f.write(f"# Digest: {basename}\n\n")
        f.write(f"- **Source**: `{filepath}`\n")
        f.write(f"- **Extracted at**: {now}\n")
        f.write(f"- **Chunks**: {total_chunks}\n")
        f.write(f"- **Format**: {ext}\n\n---\n\n")
        for i, chunk in enumerate(chunks, 1):
            f.write(f"<!-- chunk:{i}/{total_chunks} section:{chunk['section']} -->\n")
            f.write(f"## Chunk {i}: {chunk['section']}\n\n")
            f.write(chunk["content"])
            f.write("\n\n---\n\n")

    # Update index
    index = load_index(store_path)
    index["documents"][filepath] = {
        "sha256": file_hash,
        "extracted_at": now,
        "digest_file": digest_filename,
        "basename": basename,
        "format": ext,
        "chunks": total_chunks,
        "sections": [c["section"] for c in chunks],
    }
    save_index(store_path, index)

    summary = {
        "file": basename,
        "format": ext,
        "chunks": total_chunks,
        "sections": list({c["section"] for c in chunks}),
        "digest": digest_filename,
        "hash": file_hash[:16],
    }
    print(f"   [OK] {total_chunks} chunks -> {digest_filename}")
    return summary


def refresh_store(store_path: str) -> list[dict]:
    """Re-ingest stale documents whose source hash has changed."""
    index = load_index(store_path)
    results = []
    for filepath, entry in list(index["documents"].items()):
        if not os.path.exists(filepath):
            print(f"[WARN] Source missing, skipping: {filepath}", file=sys.stderr)
            continue
        current_hash = sha256_file(filepath)
        if current_hash != entry["sha256"]:
            print(f"[REFRESH] Stale: {entry['basename']} -- re-ingesting")
            result = ingest_file(filepath, store_path)
            results.append(result)
        else:
            print(f"   [OK] Current: {entry['basename']}")
    if not results:
        print("All documents are up to date.")
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Digest documents into .context-store")
    parser.add_argument("files", nargs="*", help="File paths or globs to ingest")
    parser.add_argument("--store", required=True, help="Path to .context-store directory")
    parser.add_argument("--refresh", action="store_true", help="Re-ingest stale documents")
    args = parser.parse_args()

    os.makedirs(args.store, exist_ok=True)

    if args.refresh:
        results = refresh_store(args.store)
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    if not args.files:
        print("ERROR: No files specified. Provide file paths/globs or use --refresh.", file=sys.stderr)
        sys.exit(1)

    # Expand globs
    expanded = []
    for pattern in args.files:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            expanded.extend(matches)
        elif os.path.exists(pattern):
            expanded.append(pattern)
        else:
            print(f"[WARN] No match for pattern: {pattern}", file=sys.stderr)

    if not expanded:
        print("ERROR: No files found after expanding patterns.", file=sys.stderr)
        sys.exit(1)

    results = []
    for filepath in expanded:
        result = ingest_file(filepath, args.store)
        results.append(result)

    # Print summary as JSON for the agent to parse
    print("\n--- EXTRACTION SUMMARY ---")
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
