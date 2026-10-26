---
name: prepare-for-commit
description: Synthesize codebase delta into README.md and docs.md, audit git status, and generate shell-safe, bulleted conventional commits. Use when the user asks to prepare for commit, stage work, empacar, or commit changes.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Empacar (Pack & Document)

**Empacar** is the process of synthesizing the development **delta** since the last commit into clean, developer-facing documentation, leaving the workspace ready for commit.

> [!IMPORTANT]
> **Do NOT interview the user.** Derive all changes from git status/diff, codebase files, and session history.

---

## Process

### Step 1 — Analyze Delta
Inspect the workspace to determine all additions, modifications, and removals.
- Run `git status` to locate modified, staged, or untracked files.
- Run `git diff HEAD` to extract exact code changes.
- Identify new features, bug fixes, database schema updates, or configuration shifts.
- Cluster changes by functional domain or bounded context (topic) to evaluate whether an advisory multi-commit split is warranted.
- Keep the project's domain vocabulary (e.g., use "Dispensación" instead of "order").

**Completion criterion**: A bulleted summary of all code changes using the project's exact domain terminology, clustered by topic if multiple domains were touched.

---

### Step 2 — Update README.md
Ensure `README.md` matches the updated codebase layout and feature set by following [README-FORMAT.md](README-FORMAT.md):
- **Features**: Update/add bullets for newly complete features.
- **Tech Stack**: Update dependencies if changed.
- **Project Structure**: Update directory mappings in `src/` if changed.
- **Endpoints**: Document new API routes.
- **Workflows**: List any new `.agent/workflows/` skills.

**Completion criterion**: A saved `README.md` containing only accurate, non-marketing technical updates.

---

### Step 3 — Update docs.md
Ensure `docs.md` guides future maintainers through the technical architecture by following [DOCS-FORMAT.md](DOCS-FORMAT.md):
- **Architecture & Design**: Document new layers, patterns (e.g., guards, strategies), or module boundaries.
- **Data Flows & Models**: Detail schema updates (columns, relations, enums) and end-to-end flows.
- **External Integrations**: Document new SDKs or third-party service connections.

**Completion criterion**: A saved `docs.md` with dense, technical documentation of all design and model changes.

---

### Step 4 — Stage for Commit
Prepare the copyable git commands for manual execution by the user.

1. **Inspect and Cluster by Topic**:
   - Run `git status` to output a clean overview of modified, untracked, and deleted files.
   - Evaluate whether the changes span multiple decoupled domains or architectural concerns (e.g., `cultivo` vs `contrato-dispensacion` vs `tesoreria`).

2. **Topic-Based Segmentation (Advisory Only)**:
   - **Professional Engineering Standard**: When changes span independent functional domains, recommend splitting them into topic-based commits following software engineering best practices (Separation of Concerns / Atomic Commits).
   - **Topic Over Size/Importance**: Segmentation must be strictly **by topic or bounded context**, NEVER by file size, line count, or perceived importance. Do NOT split a feature into "big file" vs "small file" or "core logic" vs "secondary edits"; all changes for a given functional theme stay together.
   - **Advisory Only (Human Discretion)**: Multi-commit splitting is strictly an advisory recommendation. If the human prefers a single mass commit, that is 100% valid and supported. When multiple topics exist, ALWAYS provide both options:
     - **Option A (Recommended — Segmented Commits by Topic)**: Ordered sequence of topic pairs (single-line `git add` + bulleted `git commit`).
     - **Option B (Alternative — Unified Mass Commit)**: A single mass `git add` and `git commit` grouping all modified files in one shot.
   - If all changes belong to a single cohesive topic, output only the single unified commit.

3. **Single-Line `git add` Rule (Cross-Shell Safety)**:
   - Output every `git add` command strictly on a **single continuous line** without line-breaks or backslashes (`\`).
   - > [!WARNING]
     > **NEVER use multi-line backslashes (`\`)**. In Windows PowerShell, `\` is not a line-continuation character. Pasting lines ending in `\` causes PowerShell to execute each line independently; file paths like `.docx` or `.pdf` are then invoked by Windows as system commands, popping up Microsoft Word or PDF readers. Keep `git add` strictly on one line:
     > ```powershell
     > git add path/to/file1 path/to/file2 path/to/dir
     > ```

4. **Multi-Flag `git commit` Rule (Clean Bulleted Human History)**:
   - Formulate every commit command using multiple `-m` arguments on a single line or copyable block:
     - **Title/Header**: The first `-m "<type>(<scope>): <summary>"` in lowercase imperative mood.
       *Types*: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`.  
       *Scope*: Specific module/domain (e.g., `contrato-dispensacion`, `planta`).
     - **Body Bullet Points**: Each technical change MUST be passed as its own `-m "- <bullet point>"` flag.
   - > [!WARNING]
     > **NEVER output an unformatted wall of prose or a single continuous paragraph**. Passing multiple `-m "- ..."` flags instructs Git to separate items into distinct bullet paragraphs, rendering clean, human-readable bullet lists (`• Item 1`, `• Item 2`) in GitHub, GitLens, and VS Code.
   - **Canonical Commit Syntax**:
     ```powershell
     git commit -m "<type>(<scope>): <short summary>" -m "- Technical change or ticket closed" -m "- Architecture pattern or database schema shift" -m "- Resilience, security or edge-case handling" -m "- Documentation or spec updates"
     ```

> [!CAUTION]
> **Do NOT run `git add` or `git commit` automatically.** Only output the proposed command in a code block for the user.
> **Do NOT include any AI attribution, model names, or co-authorship trailers.** The message must remain 100% human-facing and professional.

**Completion criterion**: Copyable code blocks displayed containing: (1) single-line `git add` commands completely free of backslashes or line breaks, and (2) `git commit` commands using multiple `-m` flags with clean `- ` bullet points, strictly free of prose paragraphs, AI signatures, or co-authorship trailers. If changes span multiple domains, both Option A (topic-based split) and Option B (unified all-in-one commit) are clearly provided.

---

## Guardrails
- **No draft features**: Do not document experimental or incomplete changes.
- **No speculation**: Only document verifiable code and designs present in the workspace.
- **No Arbitrary Slicing**: When recommending multiple commits, segment strictly by functional topic/domain, never by file size, line count, or perceived importance.
- **No Multi-Line `git add`**: Never output multi-line commands using `\` or `` ` `` for staging files.
- **No Wall-of-Text Commit Messages**: Never concatenate technical descriptions into a single run-on paragraph or single `-m` string. Every bullet must be isolated in its own `-m "- <point>"` flag.
- **ABSOLUTE PROHIBITION of AI Co-Authorship & Model Trailers**:
  Under NO circumstances may the commit message include trailers, tags, signatures, or mentions of AI assistants, models, or vendor providers:
  - ❌ **STRICTLY FORBIDDEN**:
    - `Co-authored-by: Claude <noreply@anthropic.com>` or any other `Co-authored-by:` line.
    - Mentions of models: *"hecho con Gemini 3.8 Flash"*, *"hecho con Claude Opus 5.5 (medium)"*, *"GPT-4"*, etc.
    - Mentions of vendors or platforms: *"Anthropic"*, *"Google"*, *"OpenAI"*, *"Antigravity"*, etc.
    - Phrases such as *"Generated with..."*, *"Assisted by..."*, *"AI-generated"*, etc.
  - ✅ **MANDATORY**:
    - Commit messages must follow standard Conventional Commits (`type(scope): summary`).
    - The commit body must describe strictly technical business/code rationale.


