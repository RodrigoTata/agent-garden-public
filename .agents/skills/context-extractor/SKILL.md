---
name: context-extractor
description: Digest binary documents (PDF, Excel, Word, PowerPoint, CSV) into a retrievable local knowledge base. Use when the user wants to read documents for context, extract information from files the agent can't open natively, mentions "digest", "extract context", "read this PDF/Excel/Word", or when another skill needs document context without re-parsing originals.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Context Extractor

**Digest** documents into chunked markdown stored in `.context-store/` at the workspace root. Subsequent reads hit the store instead of re-parsing originals — a local-first RAG pattern that saves tokens.

The store lives in the **workspace** (never in AgentGarden), so each project keeps its own digested context. `.context-store/` should be committed to git as auxiliary project context.

---

## Step 0 — Bootstrap

Before any extraction, verify the Python environment has the required libraries. Run:

```
pip install -r <AgentGarden>/.agents/skills/context-extractor/scripts/requirements.txt
```

Where `<AgentGarden>` is the absolute path to the AgentGarden workspace (wherever it lives on this machine).

**Completion criterion**: The `pip install` command exits with code 0. If it was already satisfied, move on silently. Only run this step once per session — skip it on subsequent invocations within the same conversation.

---

## Step 1 — Detect Branch

Three branches — pick the one that matches the user's intent:

| Branch | Trigger | Go to |
|---|---|---|
| **Ingest** | User provides document paths, or asks to "read/digest/extract" a file | Step 2 |
| **Query** | User asks a question and `.context-store/index.json` exists | Step 3 |
| **Refresh** | User says "refresh" or "re-digest", or the agent detects stale entries in the index | Step 4 |

If the store doesn't exist yet and the user asks a question about documents, switch to **Ingest** first, then **Query**.

---

## Step 2 — Ingest

Run the extraction script on each document path:

```
python <AgentGarden>/.agents/skills/context-extractor/scripts/extract.py "<file_path>" --store "<workspace>/.context-store"
```

The script accepts globs (`docs/*.xlsx`) and multiple paths. It detects format automatically and writes chunked markdown to the store.

For format-specific extraction rules and edge cases, consult [FORMATS.md](FORMATS.md).

After extraction, **read the generated digest file** and present a concise summary to the user: document title, number of chunks, key sections found, and any extraction warnings.

**Completion criterion**: Every requested file has a corresponding entry in `.context-store/index.json` with a current SHA-256 hash, and the user has received a summary of what was digested.

---

## Step 3 — Query

Run the query script to retrieve relevant chunks:

```
python <AgentGarden>/.agents/skills/context-extractor/scripts/query.py "<question>" --store "<workspace>/.context-store" --top 5
```

The script returns the top-N most relevant chunks as markdown. Read the output, then use those chunks as context to answer the user's question. **Do not re-read the original documents** — the digested chunks are the source of truth for token efficiency.

If the query returns no relevant results, tell the user and suggest ingesting additional documents.

**Completion criterion**: The agent has answered the user's question using only the retrieved chunks (or explicitly stated that no relevant context was found).

---

## Step 4 — Refresh

Run the extraction script with the `--refresh` flag:

```
python <AgentGarden>/.agents/skills/context-extractor/scripts/extract.py --refresh --store "<workspace>/.context-store"
```

This re-ingests any document whose source file has a different SHA-256 hash than what's recorded in `index.json`. Unchanged documents are skipped.

**Completion criterion**: `index.json` entries all have current hashes matching their source files.

---

## Guardrails

- **Never read original documents when the store already has a current digest.** The whole point is token savings.
- **Keep `.context-store/` tracked in git.** It serves as the persistent auxiliary context repository for agents and team members.
- **Bootstrap is mandatory on first run.** If `pip install` fails, stop and tell the user what's missing.
- **Chunk boundaries preserve structure.** Tables stay intact, headings stay with their content. See [FORMATS.md](FORMATS.md) for per-format rules.
