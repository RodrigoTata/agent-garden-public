# Repository Manifest

The standard layout for a GitHub-ready repository. Items marked **required** must exist before the repo is considered formatted. Items marked **recommended** should exist once the project has code. Items marked **optional** are situational.

---

## Root files

| File | Status | Purpose |
|------|--------|---------|
| `README.md` | **Required** | Project face — see [README-TEMPLATE.md](README-TEMPLATE.md) |
| `.gitignore` | **Required** | Exclude build artifacts, secrets, OS metadata |
| `LICENSE` | **Required** | Legal terms for use and distribution |
| `CHANGELOG.md` | Recommended | Notable changes per version (once releases begin) |
| `CONTRIBUTING.md` | Optional | Contributor guidelines (multi-contributor projects) |
| `CODE_OF_CONDUCT.md` | Optional | Community standards (open-source projects) |

## Root directories

| Directory | Status | Purpose |
|-----------|--------|---------|
| `src/` (or language convention: `app/`, `lib/`, package name) | Recommended | Primary source code |
| `tests/` (or `test/`, `__tests__/`) | Recommended | Test suites |
| `docs/` | **Required** | Design documents, specs, ADRs, architecture notes |
| `.github/` | Optional | GitHub-specific configs: issue templates, PR templates, Actions workflows |
| `scripts/` | Optional | Build, deploy, or utility scripts |

## docs/ contents

| File | Status | Purpose |
|------|--------|---------|
| `architecture.md` | **Required** | High-level architecture, layers, module boundaries |
| `adr/` | Optional | Architectural Decision Records (one `.md` per decision) |
| Specs, designs, diagrams | Optional | Relocated from root — design docs live here, not loose |

## Files that should NOT be in the repo

These are common clutter. Flag them as **suspect** during tidy:

- Build outputs: `dist/`, `build/`, `*.pyc`, `__pycache__/`, `node_modules/`
- OS metadata: `.DS_Store`, `Thumbs.db`, `desktop.ini`
- IDE user settings: `.idea/workspace.xml`, `.vscode/settings.json` (unless shared intentionally)
- Environment secrets: `.env`, `.env.local`, `*.key`, `*.pem`
- Temp files: `*.tmp`, `*.swp`, `*.bak`, `~$*`
- Duplicates: files with `(copy)`, `(1)`, `- Copy` in the name
