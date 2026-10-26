# Research: authoring "master" skills for Claude Code + Google Antigravity

Researched 2026-09-26 from primary sources only. Every claim has its source URL next to it.
Labels: **[INFERENCE]** = my deduction from the cited facts; **[UNDOCUMENTED]** = no primary source covers it; **[OBSERVED]** = seen in this environment, not in docs.

Source shorthand (every link below is a full URL):
- SPEC = https://agentskills.io/specification
- AS-CLIENT = https://agentskills.io/client-implementation/adding-skills-support
- AS-BP = https://agentskills.io/skill-creation/best-practices
- AS-DESC = https://agentskills.io/skill-creation/optimizing-descriptions
- AS-SCRIPTS = https://agentskills.io/skill-creation/using-scripts
- CC-SKILLS = https://code.claude.com/docs/en/skills
- CC-MCP = https://code.claude.com/docs/en/mcp
- CC-PERM = https://code.claude.com/docs/en/permissions
- CC-SUB = https://code.claude.com/docs/en/sub-agents
- A-OVERVIEW = https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (docs.claude.com redirects here)
- A-BP = https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- GH-VALIDATE = https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py
- GH-CREATOR = https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- AG-SKILLS = https://antigravity.google/docs/skills
- AG-WF2S = https://antigravity.google/docs/migration/workflows-to-skills/
- AG-MCP = https://antigravity.google/docs/mcp
- AG-PERM = https://antigravity.google/docs/permissions
- AG-PLUGINS = https://antigravity.google/docs/plugins
- AG-SUB = https://antigravity.google/docs/subagents
- AG-RULES = https://antigravity.google/docs/rules
- AG-GCLI = https://antigravity.google/docs/cli/gcli-migration
- MCP-AUTH = https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization
- MCP-CBP = https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices
- MCP-SKILLS = https://modelcontextprotocol.io/docs/develop/build-with-agent-skills

---

## 1. Agent Skills format (open standard + Anthropic constraints)

### 1.1 Frontmatter fields

| Field | Req? | Constraint | Source |
|---|---|---|---|
| `name` | Yes (spec) | 1-64 chars; only `a-z`, `0-9`, `-`; no leading/trailing hyphen; no `--`; **must match parent directory name** | https://agentskills.io/specification |
| `name` (Anthropic extra) | — | no XML tags; must not contain reserved words `anthropic`, `claude` | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| `description` | Yes | 1-1024 chars, non-empty; say what it does AND when to use it; include task keywords | https://agentskills.io/specification |
| `description` (Anthropic extra) | — | no XML tags | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |
| `description` (validator) | — | Anthropic's `quick_validate.py` rejects any `<` or `>` in description | https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py |
| `license` | No | license name or bundled file name, keep short | https://agentskills.io/specification |
| `compatibility` | No | 1-500 chars; environment requirements (product, packages, network); "most skills do not need" it | https://agentskills.io/specification |
| `metadata` | No | map string→string; use reasonably unique keys | https://agentskills.io/specification |
| `allowed-tools` | No | space-separated pre-approved tools, e.g. `Bash(git:*) Read`; **experimental**, support varies | https://agentskills.io/specification |

- Exactly these six keys are allowed by Anthropic's packager/validator; anything else fails with `Unexpected key(s) in SKILL.md frontmatter` (https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py, https://code.claude.com/docs/en/skills).
- The spec says nothing about unknown keys. The client-implementation guide recommends **lenient** loading: name/dir mismatch → warn and load; name > 64 → warn and load; missing/empty description → skip; unparseable YAML → skip (https://agentskills.io/client-implementation/adding-skills-support).
- YAML gotcha: unquoted values with a colon (`description: Use when: ...`) are invalid YAML; some clients add a fallback, don't rely on it (https://agentskills.io/client-implementation/adding-skills-support). Quote such descriptions or use a block scalar.

### 1.2 Directory conventions
```
skill-name/
├── SKILL.md      # required
├── scripts/      # executable code (self-contained or documented deps, helpful errors, handle edge cases)
├── references/   # docs loaded on demand (REFERENCE.md, FORMS.md, domain files); keep each focused
├── assets/       # templates, images, data files, schemas
└── ...           # anything else allowed
```
(https://agentskills.io/specification)
- File references: relative paths from skill root; keep references **one level deep** from SKILL.md (https://agentskills.io/specification, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- Reference files > 100 lines: put a table of contents at top (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices); skill-creator says > 300 lines (https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).
- Use forward slashes in paths, even on Windows (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- Name files descriptively (`form_validation_rules.md`, not `doc2.md`); organise by domain (`reference/finance.md`) (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

### 1.3 Progressive disclosure and budgets

| Level | Loaded | Budget | Source |
|---|---|---|---|
| 1 Metadata (name+description) | at startup, all skills | ~100 tokens/skill (spec, Anthropic); ~50-100 (client guide) | https://agentskills.io/specification, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview, https://agentskills.io/client-implementation/adding-skills-support |
| 2 SKILL.md body | on activation | < 5,000 tokens recommended | https://agentskills.io/specification |
| 3 Resources | when referenced | none until read; scripts cost only their output | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview |

- **SKILL.md < 500 lines** (spec, Anthropic best practices, Claude Code docs all agree) (https://agentskills.io/specification, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, https://code.claude.com/docs/en/skills).
- Tell the agent *when* to load each file ("Read `references/api-errors.md` if the API returns non-200"), not "see references/" (https://agentskills.io/skill-creation/best-practices).
- Validation tool: `skills-ref validate ./my-skill` (https://agentskills.io/specification).

---

## 2. Claude Code-specific features

### 2.1 Extra frontmatter (Claude Code accepts all; all optional; only `description` recommended)
Source for whole table: https://code.claude.com/docs/en/skills

| Field | Semantics |
|---|---|
| `name` | Optional; defaults to directory name; sets `/command`. Directory name **also** still invokes it. Not required to match dir. |
| `description` | If omitted, first non-empty body line is used. `description`+`when_to_use` truncated at **1,536 chars** in listing (cap configurable via `skillListingMaxDescChars`). |
| `when_to_use` | Extra trigger phrases, appended to description, shares the 1,536 cap. |
| `argument-hint` | Autocomplete hint, e.g. `[issue-number]`. |
| `arguments` | Named positional args for `$name` substitution. |
| `disable-model-invocation` | `true` = only user can invoke; description removed from Claude's context; can't be preloaded into subagents; won't run as scheduled-task prompt. |
| `user-invocable` | `false` = hidden from `/` menu, Claude-only. |
| `allowed-tools` | Tools usable without a prompt **for the invoking turn only** (clears at next user message). String (space/comma) or YAML list. Deny rules still win. |
| `disallowed-tools` | Tools removed while skill active (same scope). |
| `model` / `effort` | Per-turn override (`effort`: low/medium/high/xhigh/max). |
| `context: fork` + `agent` + `background` | Run in isolated subagent (no conversation history); `agent` defaults to `general-purpose`; `background: false` waits (v2.1.218+). |
| `hooks` | Hooks registered on invocation, persist for session. |
| `paths` | Globs; auto-load only when working with matching files. |
| `shell` | `bash` (default) or `powershell` for `` !`cmd` `` blocks. `shell: bash` on Windows without Git Bash fails the invocation. |
| `metadata`, `license`, `compatibility` | Accepted, not acted upon. |

- Unknown keys: "Claude Code ignores a field it doesn't recognize without reporting an error" (https://code.claude.com/docs/en/skills).
- Frontmatter only recognized if `---` is on line 1; malformed YAML → skill loads with empty metadata (slash command works, auto-trigger doesn't); debug with `--debug` or `claude plugin validate ~/.claude/skills` (v2.1.233+) (https://code.claude.com/docs/en/skills).
- Booleans accept yes/no/on/off/1/0 (v2.1.218+) (https://code.claude.com/docs/en/skills).
- Uploading to claude.ai / Skills API / `package_skill.py` accepts **only the six spec fields** (hard error otherwise); dynamic context injection doesn't work there (https://code.claude.com/docs/en/skills).

### 2.2 Substitutions (https://code.claude.com/docs/en/skills)
- `$ARGUMENTS` full string; if no placeholder consumes args, Claude Code appends `ARGUMENTS: <value>`.
- `$ARGUMENTS[N]` / `$N` 0-based, shell-style quoting; missing indexed arg stays literal; missing named arg → empty string.
- `${CLAUDE_SKILL_DIR}` (skill folder), `${CLAUDE_PROJECT_DIR}` (v2.1.196+), `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`, plugin-only `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`.
- `${CLAUDE_SKILL_DIR}` is also expanded inside `allowed-tools` Bash rules → pattern `allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/x.sh *)` runs a bundled script without a prompt.
- Escape a literal `$1` as `\$1`.

### 2.3 Dynamic context injection (https://code.claude.com/docs/en/skills)
- Inline `` !`cmd` `` (the `!` must start a line or follow whitespace) or fenced block opened with ```` ```! ````. Runs **before** Claude sees the skill; output replaces placeholder; not re-scanned.
- Runs in the session's current working dir (use `${CLAUDE_SKILL_DIR}`), 2-minute timeout, stderr merged.
- Non-zero exit or permission denial **aborts the whole invocation** (auto mode: unmatched commands don't abort).
- Disabled by `"disableSkillShellExecution": true`; never runs for skills synced from claude.ai.

### 2.4 Discovery (https://code.claude.com/docs/en/skills)
- Locations: Enterprise (managed dir) > Personal `~/.claude/skills/<name>/SKILL.md` > Project `.claude/skills/<name>/SKILL.md` (same-name precedence in that order). Also nested `<subdir>/.claude/skills` (loaded when Claude first touches files there), `--add-dir` dirs, plugins (`/plugin:skill`), claude.ai-synced (`~/.claude/skills/synced/`).
- Project skills are searched from cwd up to repo root.
- Claude Code docs list **no `.agents/skills` location** → it does not read the repo's `.agents/skills` natively (https://code.claude.com/docs/en/skills); the agentskills.io guide notes only that "some implementations" scan `.claude/skills` and `.agents/skills` (https://agentskills.io/client-implementation/adding-skills-support). Hence the junction is required. [INFERENCE]
- **Symlinks**: "a `<skill-name>` entry in the enterprise, personal, or project location can be a symlink to a directory elsewhere on disk. Claude Code reads `SKILL.md` from the target and loads the skill once even if several locations point at the same target" (https://code.claude.com/docs/en/skills). Windows **junctions** are not mentioned [UNDOCUMENTED]; they resolve transparently for most file APIs, so expect them to behave like directory symlinks [INFERENCE] (the existing junction setup in this repo appears to work, e.g. skills from `.agents/skills` show up in this session's skill list [OBSERVED]).
- Reserved folder names: `synced`, `anthropic-skills*` (https://code.claude.com/docs/en/skills).
- `.claude/commands/*.md` still works; skill wins on same name (https://code.claude.com/docs/en/skills).

### 2.5 Live reload (https://code.claude.com/docs/en/skills)
- "When you add, edit, or remove a skill under `~/.claude/skills/`, the project `.claude/skills/`, or a `.claude/skills/` inside an `--add-dir` directory, Claude Code picks up the change within the current session, without a restart." (Not in bare mode.)
- A **top-level** skills directory that didn't exist at session start needs `/reload-skills` (and again after every later change there).
- Detection covers SKILL.md text only; plugin hooks/.mcp.json/agents need `/reload-plugins`.
- So a new junction `~/.claude/skills/<new-skill>` created by the meta-skill should appear in the same session, because `~/.claude/skills/` already exists. Whether the watcher sees later edits made *inside the junction target* is [UNDOCUMENTED]; fallback is `/reload-skills`. [INFERENCE]

### 2.6 Listing budget and lifecycle (https://code.claude.com/docs/en/skills)
- Listing always has every name; descriptions are dropped (least-used first) when the listing exceeds its budget = **1% of the model's context window**. Raise via `skillListingBudgetFraction` (e.g. `0.02`) or `SLASH_COMMAND_TOOL_CHAR_BUDGET` (fixed char count); set low-priority skills to `"name-only"` in `skillOverrides`. Check with `/doctor`, `/context`, `/skill-doctor`.
- After invocation the body stays in context for the session (it is not re-read on later turns → write standing instructions). On auto-compaction each re-attached skill keeps its first **5,000 tokens**, combined **25,000 tokens**, most-recent first.
- Re-invoking with identical rendered content adds only a note; changed args/injection output re-append the full body.
- Permission rules: `Skill(name)`, `Skill(name *)`; deny `Skill` disables all.
- Subagents can preload skills via `skills:` in the agent file (full body injected); skills with `disable-model-invocation: true` can't be preloaded (https://code.claude.com/docs/en/sub-agents).

---

## 3. Google Antigravity skills

### 3.1 Locations (https://antigravity.google/docs/skills)

| Surface | Workspace | Global |
|---|---|---|
| Antigravity 2.0 | `<workspace-root>/.agents/skills/<skill-folder>/` | `~/.gemini/config/skills/<skill-folder>/` |
| Antigravity CLI (`agy`) | `<workspace-root>/.agents/skills/<skill-folder>/` | `~/.gemini/antigravity-cli/skills/<skill-folder>/`; plugins `~/.gemini/antigravity-cli/plugins/<name>/skills/` |
| Antigravity IDE | `<workspace-root>/.agents/skills/<skill-folder>/` | `~/.gemini/config/skills/<skill-folder>/` (legacy `~/.gemini/antigravity/skills/` also supported) |

- Default is `.agents/skills`; `.agent/skills` kept for backward compatibility (https://antigravity.google/docs/skills).
- Gemini CLI's `.gemini/skills/` is **not** read; must be moved to `.agents/skills/` (https://antigravity.google/docs/cli/gcli-migration).
- Plugins: workspace `.agents/plugins/`, global `~/.gemini/config/plugins/`; a plugin has `plugin.json`, optional `mcp_config.json`, `hooks.json`, `skills/`, `agents/`, `rules/` (https://antigravity.google/docs/plugins). No mention of `.claude-plugin/` compatibility [UNDOCUMENTED].
- Workspace `.agents/skills` only applies when the repo is the open workspace; for skills available in every Antigravity workspace they must also be placed (or linked) in the global path above [INFERENCE from https://antigravity.google/docs/skills]. Whether Antigravity follows symlinks/junctions is [UNDOCUMENTED].
- Legacy Workflows (`.agents/workflows/*.md`, 12,000-char limit) are deprecated, retired **November 1, 2026**; skill wins on name clash (https://antigravity.google/docs/migration/workflows-to-skills/).

### 3.2 Frontmatter honored (https://antigravity.google/docs/skills)

| Field | Required | Notes |
|---|---|---|
| `name` | **No** | lowercase, hyphens; defaults to folder name |
| `description` | Yes | "what the skill does and when to use it"; write in **third person** with keywords |

- Antigravity states it adopted "the open industry standard for Agent Skills" (agentskills.io) in May 2026 (https://antigravity.google/docs/migration/workflows-to-skills/).
- The same page claims skills "can define specialized system prompts, tool requirements, and delegate sub-tasks to custom subagents directly from the skill bundle", but no frontmatter keys for that are documented [UNDOCUMENTED]. Subagent files (not skills) take a `skills:` list of skill paths (https://antigravity.google/docs/subagents).
- Handling of `license`, `compatibility`, `metadata`, `allowed-tools`, or Claude-only keys: **[UNDOCUMENTED]**. The agentskills.io client guide recommends lenient parsing (https://agentskills.io/client-implementation/adding-skills-support), so ignoring is likely [INFERENCE], not guaranteed.
- No Antigravity docs for `$ARGUMENTS`, `` !`cmd` ``, `${CLAUDE_SKILL_DIR}` → treat as literal text in Antigravity [INFERENCE].
- Documented folder names: `scripts/`, `examples/`, `resources/` (https://antigravity.google/docs/skills); the migration guide also uses `references/` (https://antigravity.google/docs/migration/workflows-to-skills/).

### 3.3 Activation and behavior
- Progressive disclosure: names+descriptions at conversation start → reads full SKILL.md if relevant → executes (https://antigravity.google/docs/skills).
- Manual: `/<skill-name>` in 2.0/CLI; CLI auto-converts every skill to a slash command "immediately" on creation (https://antigravity.google/docs/skills). `/migrate-workflows` "immediately" activates new skills (https://antigravity.google/docs/migration/workflows-to-skills/). General live-reload guarantees for hand-created skills: [UNDOCUMENTED].
- Inspect active skills: Customizations menu (IDE) / `/skills` (CLI) (https://antigravity.google/docs/skills, https://antigravity.google/docs/cli/features).
- Best practices: one task per skill; specific descriptions; run scripts with `--help` as black boxes instead of reading source; add decision trees (https://antigravity.google/docs/skills).
- Budgets: rules have a 20,000-token aggregate budget "separate from the customization budget (plugins such as skills and MCP)"; the skills budget size is [UNDOCUMENTED] (https://antigravity.google/docs/rules). No documented description length limit beyond the spec's 1024.
- Permissions: files inside the workspace are auto-allowed; non-workspace files need approval (https://antigravity.google/docs/permissions) → a global skill's bundled scripts/references outside the workspace may trigger approval prompts [INFERENCE].

---

## 4. Anthropic's skill authoring best practices (condensed)
Primary: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices (A-BP). Complemented by https://agentskills.io/skill-creation/best-practices (AS-BP).

1. **Concise is key.** Context window is a public good; assume Claude is smart; per paragraph ask "does this justify its token cost?" (A-BP). "Would the agent get this wrong without this instruction? If no, cut it." (AS-BP).
2. **Degrees of freedom.** High (prose heuristics) when many approaches valid; medium (pseudocode/parameterised script) when a preferred pattern exists; low (exact script, "do not modify the command") for fragile, sequence-critical ops. Narrow-bridge vs open-field analogy (A-BP). Calibrate per section (AS-BP).
3. **Test with every model you'll use** (Haiku needs more guidance, Opus less) (A-BP).
4. **Naming**: gerund preferred (`processing-pdfs`, `analyzing-spreadsheets`); noun-phrase (`pdf-processing`) or action (`process-pdfs`) acceptable; avoid `helper`, `utils`, `documents`, reserved words, inconsistent patterns (A-BP).
5. **Descriptions**: always **third person** ("Processes Excel files…", never "I can…"/"You can…") because it is injected into the system prompt; specific, key terms, what + when; Claude chooses among 100+ skills with it (A-BP). agentskills.io adds: phrase as "Use this skill when…", focus on user intent, be "pushy" (list indirect triggers), ~a few sentences (https://agentskills.io/skill-creation/optimizing-descriptions). Skill-creator also says Claude tends to **undertrigger**, so be a bit pushy; all "when to use" info belongs in the description, not the body (https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md). Agents may not consult skills for simple one-step tasks at all (https://agentskills.io/skill-creation/optimizing-descriptions).
6. **Evaluations first**: identify gaps by running without the skill → build **3** eval scenarios → baseline → minimal instructions → iterate. Eval JSON: `skills`, `query`, `files`, `expected_behavior[]`. No built-in runner (A-BP). Trigger evals: ~20 queries (8-10 should, 8-10 near-miss shouldn't), 3 runs each, pass threshold 0.5 trigger rate; 60/40 train/test split in skill-creator's optimizer (https://agentskills.io/skill-creation/optimizing-descriptions, https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).
7. **Iterate with real usage (Claude A / Claude B)**: A authors, fresh B uses on real tasks, observe (unexpected read order, missed links, over-read files, ignored files), feed back (A-BP). Read execution traces, not only outputs (AS-BP). Start from real expertise / project artifacts, not generic LLM knowledge (AS-BP).
8. **Scripts vs instructions**: prefer scripts for deterministic/fragile ops; they're more reliable, save tokens (code never enters context, only output), consistent. State whether to **execute** ("Run `analyze_form.py`") or **read as reference** (A-BP). Bundle a script when you see the agent reinventing the same logic each run (AS-BP).
9. **Solve, don't punt** ("Solve, don't defer"): scripts handle errors themselves; no "voodoo constants" — justify every value (A-BP). Scripts must be non-interactive, support `--help`, give actionable error messages, pin versions (`npx eslint@9.0.0`), prefer self-contained deps (PEP 723 + `uv run`) (https://agentskills.io/skill-creation/using-scripts).
10. **Don't assume installed tools**: list packages and install commands (A-BP). Claude Code has full network; avoid global installs (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
11. **MCP tool references**: always fully qualified `ServerName:tool_name` (e.g. `BigQuery:bigquery_schema`) to avoid "tool not found" (A-BP). See §5 for the real Claude Code/Antigravity names.
12. **No time-sensitive info**: put superseded behavior in an "Old patterns" `<details>` section (A-BP). (Particularly relevant for fast-moving products like Power Automate/Power BI.) [INFERENCE]
13. **Consistent terminology** (one term per concept) (A-BP).
14. **Feedback loops**: run validator → fix → repeat; only proceed when validation passes; a reference doc can be the validator (A-BP, AS-BP). **Plan-validate-execute** with an intermediate file (e.g. `changes.json`) for batch/destructive ops; verbose validator errors listing valid options (A-BP).
15. **Checklists** for complex workflows that Claude copies into its response and ticks off (A-BP).
16. **Templates** (strict vs flexible), **examples** (input/output pairs), **conditional workflows**, **gotchas** section in SKILL.md (highest-value content; add every correction you had to make) (A-BP, AS-BP).
17. **Defaults, not menus** (one recommended tool + escape hatch) (A-BP, AS-BP).
18. **Procedures over declarations**: teach the method, not the one answer (AS-BP).
19. Final checklist: description specific + what/when; body < 500 lines; details split; no time-sensitive info; consistent terms; concrete examples; refs one level deep; scripts handle errors; no voodoo constants; deps listed; forward slashes; validation steps; ≥3 evals; tested on Haiku/Sonnet/Opus; real-usage tested (A-BP).
20. Security: skills are like installed software; audit bundled files; fetching external URLs is risky (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). "Principle of lack of surprise" (https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).

---

## 5. MCP: referencing tools and handling authentication

### 5.1 Tool naming differs per platform
| Context | Form | Source |
|---|---|---|
| Anthropic authoring guidance (prose in SKILL.md) | `ServerName:tool_name` | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices |
| Claude Code actual tool id / permissions / `allowed-tools` | `mcp__<server>__<tool>`; `mcp__<server>__*` for all tools of a server | https://code.claude.com/docs/en/permissions |
| Claude Code plugin-bundled server | `mcp__plugin_<plugin>_<server>__<tool>` | https://code.claude.com/docs/en/mcp |
| claude.ai connectors in Claude Code | e.g. `mcp__claude_ai_Google_Drive__search_files` (server "claude.ai Google Drive") | [OBSERVED] in this session's tool list |
| Antigravity permission syntax | `mcp(server/tool)`, `mcp(server/*)`, `mcp(*)`; default mode **Ask** | https://antigravity.google/docs/mcp, https://antigravity.google/docs/permissions |

- The runtime tool-name format the Antigravity *model* sees is [UNDOCUMENTED].
- Recommendation for dual-platform skills: name the server and the tool in prose and give both forms once, e.g. "Use the `sharepoint` server's `list_files` tool (Claude Code: `mcp__sharepoint__list_files`; Antigravity permission: `mcp(sharepoint/list_files)`)" [INFERENCE]. Server names are user-chosen config keys, so a skill should tell the agent to discover the actual server name if the expected one is absent [INFERENCE].
- Claude Code defers MCP tool definitions by default (tool search); only names + server instructions load at start (https://code.claude.com/docs/en/mcp). A skill can tell the agent to search/load the tool before calling it [INFERENCE].

### 5.2 Configuration and auth
- **Claude Code**: scopes local (`~/.claude.json`), project (`.mcp.json`, committed), user (`~/.claude.json`) (https://code.claude.com/docs/en/mcp). Remote servers returning 401/403 are flagged; user authenticates via `/mcp` (OAuth 2.0); startup notice lists servers needing sign-in; token refresh retried once (https://code.claude.com/docs/en/mcp).
- **Non-interactive Claude Code** (`claude -p`, Agent SDK, subagents): no `/mcp` panel, OAuth can't run; Claude is told the server's tools are unavailable until authorized (v2.1.196+) (https://code.claude.com/docs/en/mcp). [OBSERVED] this very session received such a notice for "claude.ai Microsoft 365" and several plugin servers.
- claude.ai connectors in cloud sessions must be re-authorized at claude.ai/customize/connectors, not in-session (https://code.claude.com/docs/en/mcp).
- **Antigravity**: `~/.gemini/config/mcp_config.json` (global) and `.agents/mcp_config.json` (workspace); remote uses `serverUrl` (not `url`/`httpUrl`); auth via automatic OAuth for DCR servers, manual `oauth: {clientId, clientSecret}` with redirect `https://antigravity.google/oauth-callback`, `authProviderType: "google_credentials"` (ADC), or `headers`; authenticate in Agent Settings → Customizations → Authenticate; tokens in `~/.gemini/antigravity/mcp_oauth_tokens.json`; `disabledTools` list supported (https://antigravity.google/docs/mcp).
- **MCP protocol**: remote servers use OAuth 2.1 and answer `401` + `WWW-Authenticate` pointing to Protected Resource Metadata; stdio servers use env/embedded credentials instead (https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/authorization).

### 5.3 Skills + MCP combined
- MCP docs: "a skill file can declare which MCP servers it needs, and the host connects them only when that skill is invoked" (https://modelcontextprotocol.io/docs/2026-07-28/develop/clients/client-best-practices) — no standard frontmatter key exists for this in the spec (https://agentskills.io/specification) [UNDOCUMENTED how]; use `compatibility` prose (e.g. "Requires the X MCP server") [INFERENCE].
- Bundling servers with skills: Claude Code — make the skill folder a plugin (`.claude-plugin/plugin.json`) to ship `.mcp.json` (https://code.claude.com/docs/en/skills); Antigravity — plugin with `mcp_config.json` (https://antigravity.google/docs/plugins). The two plugin formats are different [INFERENCE].
- MCP's own reference skills (`mcp-server-dev`) follow the pattern SKILL.md + `references/` of auth flows etc. (https://modelcontextprotocol.io/docs/develop/build-with-agent-skills).
- Recommended skill behavior for auth-gated servers [INFERENCE, grounded in the auth docs above]: (1) pre-flight step: check the server is connected; (2) if it needs auth, stop and tell the user exactly how to authorize (Claude Code: `/mcp` → Authenticate, or claude.ai connector settings; Antigravity: Agent Settings → Customizations → Authenticate), never ask for tokens in chat; (3) offer a documented fallback (local file export, REST via script with env-var credential, manual paste) so the skill degrades rather than failing.

---

## Compatibility checklist: skills that must run in both Claude Code and Antigravity

- [ ] Folder `.agents/skills/<name>/SKILL.md`; Claude Code reaches it via `~/.claude/skills/<name>` junction/symlink (https://code.claude.com/docs/en/skills). For Antigravity outside this repo's workspace, also link into `~/.gemini/config/skills/<name>` (2.0/IDE) and/or `~/.gemini/antigravity-cli/skills/<name>` (CLI) (https://antigravity.google/docs/skills). Symlink support in Antigravity: [UNDOCUMENTED], verify.
- [ ] `name` **present** and **equal to folder name**; `^[a-z0-9]+(-[a-z0-9]+)*$`, ≤ 64 chars; no `claude`/`anthropic` (spec requires; Antigravity/Claude Code default to folder so they never conflict) (https://agentskills.io/specification, https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview).
- [ ] `description` ≤ 1024 chars (well under Claude Code's 1,536 cap), third person, "what + Use when …" with trigger keywords (Spanish and English if the user writes both [INFERENCE]), no `<`/`>`/XML, quoted if it contains `: ` (https://agentskills.io/specification, https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py).
- [ ] Frontmatter limited to the six spec keys by default. Add Claude-only keys (`disable-model-invocation`, `argument-hint`, `context`, …) only when needed; Claude Code ignores unknown keys, Antigravity behavior is [UNDOCUMENTED], claude.ai upload rejects them (https://code.claude.com/docs/en/skills).
- [ ] `---` on line 1; valid YAML; save as UTF-8 **without BOM** and preferably **LF** line endings — Anthropic's validator regex `^---\n` fails on CRLF [INFERENCE from https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/quick_validate.py].
- [ ] Body < 500 lines / ~5k tokens; details in `references/` (one level deep, ToC if > 100 lines), templates in `assets/`, code in `scripts/` (https://agentskills.io/specification).
- [ ] No reliance on Claude-only body features (`$ARGUMENTS`, `$0`, `` !`cmd` ``, `${CLAUDE_SKILL_DIR}`); if used, write text that still makes sense when left literal [INFERENCE].
- [ ] Script paths: write them relative to the skill folder and tell the agent to resolve them against the directory containing SKILL.md (Claude Code runs commands in the session cwd, not the skill dir: https://code.claude.com/docs/en/skills; agentskills assumes skill-root-relative: https://agentskills.io/skill-creation/using-scripts). Forward slashes only.
- [ ] Scripts cross-platform (Windows here): prefer Python (PEP 723 + `uv run`) or Node over bash-only; non-interactive, `--help`, clear errors (https://agentskills.io/skill-creation/using-scripts). Bash in Claude Code on Windows needs Git Bash (https://code.claude.com/docs/en/skills).
- [ ] MCP tools referenced by server + tool name with both platform forms, plus an auth pre-flight and a fallback path (§5).
- [ ] Don't reference platform-specific tool names (`Read`, `Bash`, `view_file`, `run_command`) as hard requirements; describe the action ("read the file", "run the command") [INFERENCE from https://antigravity.google/docs/sdk/tools vs https://code.claude.com/docs/en/skills].
- [ ] No time-sensitive statements in the main body; "Old patterns" section for deprecated behavior (https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).
- [ ] Validate with `skills-ref validate` (https://agentskills.io/specification) and/or `claude plugin validate ~/.claude/skills` (https://code.claude.com/docs/en/skills); then trigger-test in both apps (`/skills` in Antigravity CLI, "What skills are available?" in Claude Code).
- [ ] After creating the junction in Claude Code, confirm it appears; else `/reload-skills` (https://code.claude.com/docs/en/skills).

## Conflicts between the platforms / sources (summary)

| Topic | Claude Code | Antigravity | Spec / Anthropic |
|---|---|---|---|
| `name` required? | No, defaults to dir (https://code.claude.com/docs/en/skills) | No, defaults to folder (https://antigravity.google/docs/skills) | Yes + must match dir (https://agentskills.io/specification) |
| Unknown keys | Silently ignored | [UNDOCUMENTED] | Validator/upload hard error (https://code.claude.com/docs/en/skills) |
| Description cap | 1,536 (desc+when_to_use) | not stated | 1,024 |
| Description voice | — | third person (https://antigravity.google/docs/skills) | third person (A-BP) vs "Use this skill when…" imperative (https://agentskills.io/skill-creation/optimizing-descriptions) → combine: "Does X. Use when …" |
| Folder names | any | `scripts/ examples/ resources/` (+`references/` in migration doc) | `scripts/ references/ assets/` |
| Script cwd | session cwd; use `${CLAUDE_SKILL_DIR}` | [UNDOCUMENTED] | skill root assumed |
| MCP tool name | `mcp__server__tool` | `mcp(server/tool)` (permissions) | `ServerName:tool_name` in prose |
| Native project path | `.claude/skills` | `.agents/skills` | not mandated; `.agents/skills` is the cross-client convention (https://agentskills.io/client-implementation/adding-skills-support) |
| Live reload | watched dirs, same session; new top-level dir → `/reload-skills` | "immediately" for CLI slash commands; otherwise [UNDOCUMENTED] | — |

## Open questions

1. Does Antigravity (2.0 / IDE / CLI) follow symlinks or Windows junctions in `.agents/skills` or `~/.gemini/config/skills`? [UNDOCUMENTED] — test empirically.
2. Does Antigravity ignore, warn on, or reject unknown frontmatter keys (e.g. `disable-model-invocation`, `argument-hint`)? [UNDOCUMENTED]
3. Does Antigravity honor `allowed-tools`, `compatibility`, `metadata`? [UNDOCUMENTED]
4. Antigravity's skill-listing/customization token budget and any description truncation length. [UNDOCUMENTED]
5. Does Antigravity pick up a skill folder created mid-conversation in 2.0/IDE without restart? Only CLI slash-command creation is described as immediate. [UNDOCUMENTED]
6. What exact tool-name string does the Antigravity model see for MCP tools (vs. the `mcp(server/tool)` permission syntax)? [UNDOCUMENTED]
7. Does Claude Code's file watcher detect edits made inside a junction target (outside `~/.claude/skills`) as it does for real folders? [UNDOCUMENTED]
8. Antigravity's "skills can define … tool requirements, and delegate sub-tasks to custom subagents" — which frontmatter keys, if any? [UNDOCUMENTED]
9. Does Antigravity run script paths relative to the skill folder or the workspace? [UNDOCUMENTED]
10. Is there a standard key for "this skill needs MCP server X" (MCP client best practices mention it; spec has none)? [UNDOCUMENTED]
