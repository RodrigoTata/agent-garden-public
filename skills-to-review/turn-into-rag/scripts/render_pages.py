#!/usr/bin/env python3
"""
turn-into-rag: render_pages.py
Render PDF pages to PNG so the agent can read scanned pages, figures and tables
that exist only as images.

Usage:
  python render_pages.py <file.pdf> <pages> [--labels] [--out DIR] [--dpi 150]

<pages> are physical page numbers (1-based position in the file, as in stage.py's
scanned-page placeholders), e.g. "12", "3,7-9" or "all". With --labels they are
printed page labels instead, the ones locators cite: "95", "xii,95".
Files are written as <out>/p-0012.png (physical numbering).
"""

import argparse
import sys
from pathlib import Path


def parse_pages(spec: str, count: int) -> list:
    if spec.strip().lower() == "all":
        return list(range(1, count + 1))
    pages = set()
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            a, b = (int(x) for x in part.split("-", 1))
            pages.update(range(a, b + 1))
        elif part:
            pages.add(int(part))
    return sorted(p for p in pages if 1 <= p <= count)


def pages_from_labels(doc, spec: str) -> list:
    pages = set()
    for label in (x.strip() for x in spec.split(",")):
        found = doc.get_page_numbers(label) if label else []
        if not found and label.isdigit():  # PDF without page labels: printed number = position
            found = [int(label) - 1]
        pages.update(i + 1 for i in found if 0 <= i < doc.page_count)
    return sorted(pages)


def main() -> int:
    p = argparse.ArgumentParser(description="Render PDF pages to PNG.")
    p.add_argument("pdf")
    p.add_argument("pages", help='physical pages: "12", "3,7-9" or "all"')
    p.add_argument("--labels", action="store_true", help="read <pages> as printed page labels")
    p.add_argument("--out", default="_pages", help="output folder (default: ./_pages)")
    p.add_argument("--dpi", type=int, default=150)
    args = p.parse_args()

    import pymupdf
    doc = pymupdf.open(args.pdf)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    pages = pages_from_labels(doc, args.pages) if args.labels else parse_pages(args.pages, doc.page_count)
    if not pages:
        print(f"No valid pages in '{args.pages}' (document has {doc.page_count}).", file=sys.stderr)
        return 1
    for n in pages:
        target = out / f"p-{n:04d}.png"
        doc[n - 1].get_pixmap(dpi=args.dpi).save(target)
        print(target.as_posix())
    doc.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
