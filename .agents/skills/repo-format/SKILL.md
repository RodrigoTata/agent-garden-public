---
name: repo-format
description: Scaffold a new project folder into a GitHub-ready repository, or tidy an existing one into standard shape.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Repo Format

**Scaffold** a bare project folder into a GitHub-ready repository, or **tidy** a disorganised repo back into standard shape. Both branches produce the same outcome: a clean, navigable layout following the manifest in [MANIFEST.md](MANIFEST.md).

> [!IMPORTANT]
> **Never delete files without explicit user approval.** When tidying, present candidates for removal and wait for confirmation.

---

## Branch: Scaffold (new project)

Use when the folder contains source material (specs, prototypes, assets) but no repo structure — no README, no `.gitignore`, no `docs/`.

### Step 1 — Survey

Walk the folder. Catalogue every file and directory. Identify:

- The project's **language/framework** (infer from file extensions, configs, or specs).
- Any existing documentation (specs, notes, design docs) that should inform the README.
- The project's **name** and **purpose** (from filenames, folder name, or document content).

**Completion criterion**: A bulleted inventory of every file in the folder with its role identified, plus the inferred language and project purpose.

---

### Step 2 — Generate .gitignore

Produce a `.gitignore` appropriate for the detected language/framework. Use GitHub's official templates as a baseline (`github/gitignore`). Add OS-specific entries (`Thumbs.db`, `.DS_Store`), IDE entries (`.idea/`, `.vscode/` settings that shouldn't be shared), and environment files (`.env`).

**Completion criterion**: A saved `.gitignore` covering the detected stack, OS artifacts, and secrets.

---

### Step 3 — Generate README.md

Write the README following the structure in [README-TEMPLATE.md](README-TEMPLATE.md). Source content from existing specs or documents in the folder — do not invent features. If information is missing, leave a `<!-- TODO: ... -->` placeholder and tell the user.

**Completion criterion**: A saved `README.md` with every section from the template either filled or marked `TODO`, and zero invented content.

---

### Step 4 — Create docs/ directory

Create `docs/` with an initial `architecture.md` if the project has enough design material (specs, ADRs, diagrams) to populate it. If the project is too early, create `docs/` with a stub `architecture.md` containing section headings only.

Move any existing design documents (specs, ADRs, diagrams) into `docs/` — do not leave them loose in the root.

**Completion criterion**: A `docs/` directory exists. Any pre-existing design documents are relocated there. `architecture.md` exists with at least section headings.

---

### Step 5 — Add LICENSE

Ask the user which license to apply. Default suggestion: MIT for personal projects, Apache 2.0 for projects with patent considerations. Generate the full license text with the correct year and copyright holder.

**Completion criterion**: A saved `LICENSE` file with the user's chosen license and correct metadata.

---

### Step 6 — Verify layout

Compare the resulting directory tree against [MANIFEST.md](MANIFEST.md). Report any missing items (with rationale for why they're absent — e.g., "no tests directory yet because no code has been written") and any extras that don't belong.

**Completion criterion**: A printed directory tree showing the final layout, with a checklist of manifest items marked present/absent/deferred.

---

## Branch: Tidy (existing repo)

Use when the repo exists but is disorganised — files in wrong places, missing standard files, stale artifacts cluttering the root.

### Step 1 — Audit

Walk the entire repo. Produce three lists:

1. **Missing**: Standard files from [MANIFEST.md](MANIFEST.md) that are absent.
2. **Misplaced**: Files that exist but live in the wrong location (e.g., a spec in the root that belongs in `docs/`, test files outside `tests/`).
3. **Suspect**: Files that appear unnecessary — build artifacts committed to the repo, duplicate files, empty files, temp files, OS metadata. Do **not** delete these — only catalogue them.

**Completion criterion**: Three complete lists (missing, misplaced, suspect) with file paths and one-line justification for each entry.

---

### Step 2 — Propose changes

Present the audit as a single numbered plan:

- **Create** missing standard files (with proposed content summary).
- **Move** misplaced files (with source → destination).
- **Delete** suspect files (each flagged for user approval).

> [!CAUTION]
> Every deletion must be individually approved by the user before execution. Batch "delete all" is not acceptable.

**Completion criterion**: A numbered plan presented to the user, with deletions clearly marked as pending approval.

---

### Step 3 — Execute approved changes

After user approval, execute the plan:

- Create missing files using the same templates as the Scaffold branch.
- Move misplaced files (update any internal references that break).
- Delete only the files the user explicitly approved.

**Completion criterion**: Every approved change executed. No unapproved deletions. Internal references updated.

---

### Step 4 — Verify layout

Same as Scaffold Step 6: compare against the manifest, print the tree, report gaps.

**Completion criterion**: A printed directory tree with manifest checklist.

---

## Guardrails

- **No invented content.** README descriptions, feature lists, and architecture docs must be derived from existing files — specs, code, comments, commit history. If the information doesn't exist, use `<!-- TODO -->`.
- **Respect existing conventions.** If the repo already uses `src/` vs `lib/`, keep it. The manifest is a guide, not a straitjacket.
- **Language match.** Write README and docs in the same language as existing documentation. If no docs exist, ask the user.
