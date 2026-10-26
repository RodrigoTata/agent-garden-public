#!/usr/bin/env python3
"""
context-extractor: query.py
Keyword search over digested documents in .context-store/.

Usage:
  python query.py "<question>" --store <store_path> [--top N]

Returns the top-N most relevant chunks as markdown, scored by keyword frequency.
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def tokenize(text: str) -> list[str]:
    """Simple word tokenizer: lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\sáéíóúñü]", " ", text)
    return [w for w in text.split() if len(w) > 1]


def load_chunks(store_path: str) -> list[dict]:
    """Load all chunks from all digest files in the store."""
    digests_dir = os.path.join(store_path, "digests")
    if not os.path.isdir(digests_dir):
        return []

    index_path = os.path.join(store_path, "index.json")
    index = {}
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            index = json.load(f)

    # Build a reverse map: digest_file -> source info
    digest_to_source = {}
    for source_path, entry in index.get("documents", {}).items():
        digest_to_source[entry["digest_file"]] = {
            "source": source_path,
            "basename": entry["basename"],
            "format": entry["format"],
        }

    chunks = []
    for filename in os.listdir(digests_dir):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(digests_dir, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        source_info = digest_to_source.get(filename, {"source": "unknown", "basename": filename, "format": "?"})

        # Split by chunk markers
        chunk_parts = re.split(r"<!-- chunk:(\d+)/(\d+) section:(.*?) -->", content)

        # chunk_parts: [preamble, chunk_num, total, section, content, chunk_num, total, section, content, ...]
        i = 1
        while i < len(chunk_parts) - 3:
            chunk_num = chunk_parts[i]
            total = chunk_parts[i + 1]
            section = chunk_parts[i + 2]
            chunk_content = chunk_parts[i + 3].strip()
            # Remove the "## Chunk N: ..." heading from the content for cleaner output
            chunk_content = re.sub(r"^## Chunk \d+:.*?\n+", "", chunk_content).strip()
            # Remove trailing ---
            chunk_content = re.sub(r"\n---\s*$", "", chunk_content).strip()

            chunks.append({
                "source": source_info["basename"],
                "source_path": source_info["source"],
                "section": section,
                "chunk_num": int(chunk_num),
                "total_chunks": int(total),
                "content": chunk_content,
                "tokens": tokenize(chunk_content),
            })
            i += 4

    return chunks


def score_chunks(query: str, chunks: list[dict]) -> list[tuple[float, dict, list[str]]]:
    """Score each chunk against the query using TF-IDF-like relevance."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    # Document frequency for IDF
    num_docs = len(chunks)
    doc_freq = Counter()
    for chunk in chunks:
        unique_tokens = set(chunk["tokens"])
        for token in unique_tokens:
            doc_freq[token] += 1

    scored = []
    for chunk in chunks:
        if not chunk["tokens"]:
            continue
        chunk_counter = Counter(chunk["tokens"])
        total_tokens = len(chunk["tokens"])
        score = 0.0
        matched_terms = []
        for qt in query_tokens:
            tf = chunk_counter.get(qt, 0) / max(total_tokens, 1)
            df = doc_freq.get(qt, 0)
            idf = math.log((num_docs + 1) / (df + 1)) + 1 if df > 0 else 0
            term_score = tf * idf
            if term_score > 0:
                matched_terms.append(qt)
            score += term_score

        # Bonus for section title match
        section_tokens = tokenize(chunk["section"])
        section_match = sum(1 for qt in query_tokens if qt in section_tokens)
        score += section_match * 0.5

        # Bonus for source name match
        source_tokens = tokenize(chunk["source"])
        source_match = sum(1 for qt in query_tokens if qt in source_tokens)
        score += source_match * 0.3

        if score > 0:
            scored.append((score, chunk, matched_terms))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored


def main():
    parser = argparse.ArgumentParser(description="Query digested documents in .context-store")
    parser.add_argument("query", help="The question or search terms")
    parser.add_argument("--store", required=True, help="Path to .context-store directory")
    parser.add_argument("--top", type=int, default=5, help="Number of top results to return")
    args = parser.parse_args()

    if not os.path.isdir(args.store):
        print(f"ERROR: Store not found at {args.store}", file=sys.stderr)
        print("Run extract.py first to ingest documents.", file=sys.stderr)
        sys.exit(1)

    chunks = load_chunks(args.store)
    if not chunks:
        print("No digested documents found in the store.")
        print("Run extract.py first to ingest documents.")
        sys.exit(0)

    results = score_chunks(args.query, chunks)

    if not results:
        print(f"No relevant chunks found for query: \"{args.query}\"")
        print(f"\nDocuments in store: {len(set(c['source'] for c in chunks))}")
        print(f"Total chunks searched: {len(chunks)}")
        sys.exit(0)

    top_results = results[:args.top]

    print(f"# Query Results: \"{args.query}\"\n")
    print(f"Searched {len(chunks)} chunks across {len(set(c['source'] for c in chunks))} documents.\n")
    print(f"Showing top {len(top_results)} results:\n")
    print("---\n")

    for i, (score, chunk, matched) in enumerate(top_results, 1):
        print(f"## Result {i} (score: {score:.3f})")
        print(f"- **Source**: `{chunk['source']}` (chunk {chunk['chunk_num']}/{chunk['total_chunks']})")
        print(f"- **Section**: {chunk['section']}")
        print(f"- **Matched terms**: {', '.join(matched)}")
        print(f"\n{chunk['content']}\n")
        print("---\n")


if __name__ == "__main__":
    main()
