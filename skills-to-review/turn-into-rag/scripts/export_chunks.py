#!/usr/bin/env python3
"""
turn-into-rag: export_chunks.py
Derive a JSONL file of retrieval chunks (one per H2 section) from the distilled
Markdown in a knowledge base, for loading into a vector store.

Usage:
  python export_chunks.py <kb-dir> [--out <kb-dir>/chunks.jsonl]

The Markdown stays the source of truth: regenerate this file after any edit.
Skips INDEX.md, ledger.md and anything under _raw/.
"""

import argparse
import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKIP = {"INDEX.md", "ledger.md"}


def parse_frontmatter(text: str):
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw, body = text[3:end], text[end + 4:].lstrip("\n")
    try:
        import yaml
        return yaml.safe_load(raw) or {}, body
    except ImportError:  # minimal "key: value" / "key: [a, b]" fallback
        meta = {}
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                v = v.strip().strip('"')
                meta[k.strip()] = [x.strip().strip('"') for x in v[1:-1].split(",")] if v.startswith("[") else v
        return meta, body


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def chunks_of(path: Path, kb: Path):
    meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    rel = path.relative_to(kb).as_posix()
    title, current, buf, in_fence, out = path.stem, None, [], False, []

    def emit(heading, text):
        out.append({
            "id": f"{rel}#{slug(heading)}",
            "source_id": meta.get("source_id") or path.parent.name,
            "file": rel,
            "title": title,
            "heading": heading,
            "locator": meta.get("locator", ""),
            "topics": meta.get("topics", []),
            "text": f"{title} › {heading}\n\n{text}",
            "metadata": meta,
        })

    def flush():
        text = "\n".join(buf).strip()
        heading = current or "(intro)"
        is_glossary = path.name == "glossary.md" or heading.lower().startswith("glossary")
        if text and is_glossary:  # one chunk per term, so "what is X?" retrieves just X
            for line in text.splitlines():
                term = re.match(r"^\*\*(.+?)\*\*", line.strip())
                if term:
                    emit(f"Glossary › {term.group(1)}", line.strip())
        elif text:
            emit(heading, text)
        buf.clear()

    for line in body.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
        if not in_fence and line.startswith("# ") and current is None and not buf:
            title = line[2:].strip()
        elif not in_fence and line.startswith("## "):
            flush()
            current = line[3:].strip()
        else:
            buf.append(line)
    flush()
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Export distilled Markdown as JSONL retrieval chunks.")
    p.add_argument("kb", help="knowledge base folder")
    p.add_argument("--out", help="output file (default: <kb>/chunks.jsonl)")
    args = p.parse_args()

    kb = Path(args.kb)
    out_path = Path(args.out) if args.out else kb / "chunks.jsonl"
    files = sorted(f for f in kb.rglob("*.md") if f.name not in SKIP and "_raw" not in f.parts)
    count = 0
    with open(out_path, "w", encoding="utf-8") as fh:
        for f in files:
            for chunk in chunks_of(f, kb):
                fh.write(json.dumps(chunk, ensure_ascii=False, default=str) + "\n")
                count += 1
    print(f"{count} chunks from {len(files)} files -> {out_path.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
