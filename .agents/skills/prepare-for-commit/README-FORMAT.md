# README Format Guide

This document defines the expected structure and writing conventions for `README.md`.

---

## Structure (in order)

1. **Title** — Project name as H1.
2. **Description** — 2–4 sentences. What the system does, who it's for, and the core workflow it enables (e.g., "seed-to-patient traceability"). No filler.
3. **Key Features** — Grouped by domain (e.g., Cultivation, Medical, Store). Each feature is a bullet with a **bold label** and a plain-English description. Focus on capabilities, not implementation details.
4. **Tech Stack** — Flat table or bullet list. Framework, Language, DB, ORM, Auth, Storage, AI, Email, Docs.
5. **Project Structure** — A `src/` tree. One line per module. Short comment on what each module owns.
6. **Main Endpoints** — Grouped by domain. Only surface-level (`POST /dispensacion/reserva`, not internal routes). Point to `/api` (Swagger) for the full list.
7. **Setup & Installation** — Prerequisites, `npm install`, env vars template, run commands (`start:dev`, `start:prod`).
8. **Agent Workflows** — List the `.agent/workflows/` skills with a one-line description each.
9. **Footer** — a one-line pointer to the project license (e.g. "Licensed under the Apache License 2.0 — see LICENSE").

---

## Writing Rules

- **Spanish only.** The skill itself is in English, but README.md and docs.md are always written in Spanish for this project.
- **No marketing language.** "Robusto", "potente", "poderoso" — delete on sight.
- **Accuracy over completeness.** An accurate short README beats an impressive stale one.
- **Module names match `src/` directory names.** Do not rename or alias them.
- **Endpoint paths must match the controllers.** Verify before writing.
