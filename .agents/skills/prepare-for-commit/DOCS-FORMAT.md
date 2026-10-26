# docs.md Format Guide

This document defines the expected structure and writing conventions for `docs.md`.

---

## Structure (in order)

1. **Title** — "Architecture Guide" as H1.
2. **Architecture Overview** — The layered architecture (Controllers → Services → Repositories). One paragraph max per layer. Note any constraints or conventions enforced at that layer.
3. **Design Patterns** — One H3 subsection per pattern. Include: what it solves, where it's used in the codebase (module names, not file paths), and what the contract looks like from the caller's perspective.
4. **Key Data Flows** — One H3 per end-to-end flow. Written as a numbered sequence of steps. Each step names the module and the action it performs. No code snippets — just plain English.
5. **External Integrations** — One bullet per integration. State: what service, what it's used for, and how the system interacts with it (webhook, SDK call, background job, etc.).
6. **Data Model** — High-level notes on the schema: key entities, non-obvious relationships, enum values that drive logic. Point to ERD or Mermaid diagram if it exists.
7. **Footer** — a one-line pointer to the project license (e.g. "Licensed under the Apache License 2.0 — see LICENSE").

---

## Writing Rules

- **Spanish only.** The skill is in English, but docs.md is always written in Spanish for this project.
- **Dense and technical.** This document is read by developers who already know NestJS and TypeORM. Don't explain basics.
- **Pattern names must match the implementation.** If the code calls it `DispensacionCleanupService`, document it under that name.
- **Data flows describe what happens, not how it's coded.** No TypeScript. No SQL. Plain English sequences.
- **Do not duplicate README.** If README covers it, reference it. docs.md is the deep-dive.
- **One source of truth.** If a business rule is documented here, it must exist in code. Remove anything that no longer applies.
