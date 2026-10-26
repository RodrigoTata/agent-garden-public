---
name: sync-agents
description: Synchronizes AgentGarden skills, rules, and multi-root VS Code workspace folders (.code-workspace) across Google Antigravity and Claude Code on any PC. Use when setting up a new machine or workspace, when slash commands (/) or rules are missing, or when the user mentions "sync-agents", "sync skills", or multi-folder workspace visibility.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Sync Agents — Dual-Agent & Multi-Root Workspace Parity

Establishes full **parity** between **Google Antigravity** and **Claude Code** across every folder in a VS Code `.code-workspace` (and globally on a new PC), ensuring both agents discover every skill via `/` and read every sibling root and `.agents/rules/` file.

## Steps

### 1. Audit Workspace Roots and Global Links

Run [`scripts/sync_agents.py`](scripts/sync_agents.py) in `--check` mode against the active workspace directory or `.code-workspace` file:

```bash
python .agents/skills/sync-agents/scripts/sync_agents.py --workspace . --check
```

Inspect the output to identify:
1. All sibling folders declared in the parent or local `.code-workspace` file.
2. Missing global skill links in `~/.gemini/config/skills` (Antigravity) and `~/.claude/skills/<skill-name>` (Claude Code).
3. Missing workspace junctions (`<folder>/.agents/skills` and `<folder>/.claude/skills`).
4. Missing or incomplete `CLAUDE.md` rule imports (`@.agents/rules/...`) and multi-root folder maps.

**Completion criterion**: `sync_agents.py --check` executed and every workspace folder, global link, and `CLAUDE.md` file accounted for.

### 2. Enforce Dual-Agent Parity

Execute [`scripts/sync_agents.py`](scripts/sync_agents.py) without `--check` to wire all missing junctions, `CLAUDE.md` imports, and `.gitignore` exclusions:

```bash
python .agents/skills/sync-agents/scripts/sync_agents.py --workspace .
```

This step performs four deterministic actions:
1. **Global Antigravity Discovery**: Links `~/.gemini/config/skills` to `AgentGarden/.agents/skills`.
2. **Global Claude Code Discovery**: Links each `AgentGarden/.agents/skills/<name>` into `~/.claude/skills/<name>` and links `AgentGarden/.claude/skills` to `AgentGarden/.agents/skills`.
3. **Workspace Folder Parity**: Links `<folder>/.agents/skills` and `<folder>/.claude/skills` to `AgentGarden/.agents/skills` in every sibling folder of the `.code-workspace`, and adds `.agents/` and `.claude/` to `<folder>/.gitignore` so junctions never dirty `git status`.
4. **Cross-Agent Rule & Multi-Root Map (`CLAUDE.md`)**: Ensures each project root has a `CLAUDE.md` that imports `.agents/rules/*.md` via `@` pointers and lists all sibling folders from the `.code-workspace` so both agents know every root in the workspace.

**Completion criterion**: `sync_agents.py` exits with code `0` and zero `MISSING` or `UPDATE` entries remain when re-run with `--check`.

### 3. Validate Skill Catalogue Integrity

Run the AgentGarden skill validator across `sync-agents` (and any newly added skills) to verify UTF-8 without BOM encoding, LF line endings, and frontmatter compliance:

```bash
python .agents/skills/study-and-be-a-master-of/scripts/install_skill.py sync-agents
```

**Completion criterion**: Validator reports `OK validación` and `OK enlazada` with zero errors.

