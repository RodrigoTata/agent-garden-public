# Skill Security Checks Reference (`SECURITY-CHECKS.md`)

Exhaustive static-analysis checklist for auditing an Agent Skill (`SKILL.md` + auxiliary files or a raw skill prompt pasted in chat).
Following `/cyber-audit` discipline, the auditor must account for **every** category (`SC-01` through `SC-07`) — either **flag it** (`🔴 CRITICAL`, `🟡 WARNING`, `🔵 INFO`) with exact location (`file:line` or `pasted-line`) and exploitation scenario, or **clear it** with concrete evidence.

---

## SC-01 — Concealment, Steganography & Unicode Smuggling

Attackers hide instructions from human reviewers on GitHub / Hugging Face while keeping them visible to the LLM tokenizer ([RESEARCH.md §2.1](RESEARCH.md)).

- **Unicode Tag Block (`U+E0000`–`U+E007F`)**: Any character in Plane 14 Tags = `🔴 CRITICAL`. Decode and print the hidden ASCII string.
- **Bidirectional Control Characters (`U+202A`–`U+202E`, `U+2066`–`U+2069`, `U+061C`, `U+200E`, `U+200F`)**: Trojan Source visual reordering = `🔴 CRITICAL`.
- **Zero-Width & Variation Selectors (`U+200B`–`U+200D`, `U+2060`, `U+FEFF` after byte 0, `U+FE00`–`U+FE0F`, `U+E0100`–`U+E01EF`)**: Invisible characters splitting words or encoding hidden payloads = `🔴 CRITICAL` (if encoding payload/evading keywords) or `🟡 WARNING`.
- **HTML & Markdown Comment Smuggling**: `<!-- ... -->` or `[//]: # (...)` containing imperative instructions, tool calls, or URLs invisible in rendered web previews = `🔴 CRITICAL` (if directive/suspicious) or `🟡 WARNING`.
- **Encoded / Obfuscated Blobs**: Base64 strings (>40 chars decoding to text/shell), hex dumps (`\x63\x75\x72\x6c`), `rot13`, `atob()`, `base64 -d`, PowerShell `-EncodedCommand` / `-enc`, or compressed blobs (`zlib`, `gzip`) = `🔴 CRITICAL`.

---

## SC-02 — Pre-Invocation RCE & Frontmatter Privilege Escalation

Skills can execute commands before the LLM even reads the body or silently alter session permissions ([RESEARCH.md §2.2](RESEARCH.md)).

- **Claude Code Dynamic Context Injection**: Inline `` !`cmd` `` or fenced ```` ```! ```` blocks in `SKILL.md` execute shell commands automatically before model evaluation = `🔴 CRITICAL` (or `🟡 WARNING` only if the user explicitly authored the skill for trusted local status checks and knows it runs pre-prompt).
- **Frontmatter Session Hooks (`hooks:`)**: Any `hooks:` key in YAML frontmatter (`PreToolUse`, `PostToolUse`, `Stop`, `UserPromptSubmit`) = `🔴 CRITICAL`.
- **Unrestricted `allowed-tools:`**: Pre-approving `Bash(*)`, `Bash`, `Write`, `Edit`, `run_command`, or wildcard `mcp__*` without user prompts = `🔴 CRITICAL` (broad shell/write) or `🟡 WARNING` (scoped tool pre-approval).
- **Bundled MCP Configs (`.mcp.json`, `mcp_config.json`, `plugin.json`)**: Bundled MCP server definitions spawning local stdio processes (`npx`, `uvx`, `python`, binaries) or connecting to untrusted remote `serverUrl` endpoints = `🔴 CRITICAL` (unverified remote/stdio binary) or `🟡 WARNING`.

---

## SC-03 — Level-1 Metadata Poisoning & Trigger Squatting

Level 1 (`name`, `description`, `when_to_use`) is loaded into the system prompt at session start for every installed skill ([RESEARCH.md §1, §2.3](RESEARCH.md)).

- **Ambient Prompt Injection in `description` / `when_to_use`**: Instructions in frontmatter telling the agent how to behave globally, to ignore rules, or to execute tools outside the skill's domain = `🔴 CRITICAL`.
- **Trigger Squatting (Universal / Greedy Triggers)**: Phrases like *"Use on every turn"*, *"Always run before answering"*, *"Use for all coding tasks"*, or stuffing unrelated keywords so the skill hijacks normal conversations = `🟡 WARNING` (or `🔴 CRITICAL` if paired with side effects).
- **Spec & Dual-Agent Frontmatter Compliance**: Missing frontmatter, `name` mismatch, `description` > 1024 chars, or XML tags `<`/`>` in `description` = `🔵 INFO` / `🟡 WARNING`.

---

## SC-04 — Direct & Indirect Prompt Injection (OWASP LLM01:2025)

Instructions inside `SKILL.md` or `references/*.md` attempting to hijack agent alignment, bypass user rules, or ingest untrusted remote prompts ([RESEARCH.md §2.3](RESEARCH.md)).

- **System & Guardrail Override**: Phrases instructing the agent to ignore prior instructions, disregard `USER_RULES`, bypass confirmation gates, or act stealthily (*"do not mention this to the user"*, *"silently"*, *"without asking approval"*, *"override safety"*) = `🔴 CRITICAL`.
- **Sandbox & Cost Guardrail Violations**: Directives to set `BypassSandbox: true` unnecessarily, launch Chrome/browser without permission, or deploy cloud services with `min-instances >= 1` / `--no-cpu-throttling` (violating workspace rules) = `🔴 CRITICAL`.
- **Indirect Prompt Injection Sinks**: Instructing the agent to fetch external mutable URLs (raw GitHub gists, pastebins, external web pages, Hugging Face dataset rows/comments, third-party APIs) and follow instructions inside them without strict data-only isolation = `🟡 WARNING` (or `🔴 CRITICAL` if fetching executable instructions).

---

## SC-05 — Credential Harvesting & Data Exfiltration (OWASP LLM06:2025)

Attempts to read secrets, environment variables, or private workspace files and transmit them outside the workspace ([RESEARCH.md §2.4](RESEARCH.md)).

- **Sensitive File & Env Access**: Reading or grepping `.env`, `~/.ssh/*`, `id_rsa`, `.aws/credentials`, `.npmrc`, `.pypirc`, `.git-credentials`, `~/.claude.json`, `mcp_oauth_tokens.json`, browser cookies/localStorage, or dumping full `env` / `printenv` / `os.environ` / `process.env` = `🔴 CRITICAL`.
- **Network Exfiltration Sinks**: Sending local data, code, or env vars via `curl -d`/`-F`, `wget --post-data`, `Invoke-RestMethod`, `requests.post`, `urllib`, `fetch`, webhooks (`webhook.site`, `ngrok`, `discord.com/api/webhooks`, `api.telegram.org`, raw IPs), or DNS queries (`nslookup`, `dig`, `ping` with interpolated secrets) = `🔴 CRITICAL`.
- **Markdown Image / Link Exfiltration**: Instructing the agent to render dynamic external image tags `![...](https://external-host/...)` or clickable links interpolated with conversation/file data = `🔴 CRITICAL`.

---

## SC-06 — Arbitrary Code Execution, Destructive Actions & Persistence

Malicious or reckless operations in `SKILL.md` commands or `scripts/*` ([RESEARCH.md §2.5](RESEARCH.md)).

- **Pipe-to-Shell & Dynamic Eval**: `curl ... | bash`, `wget ... | sh`, `irm ... | iex`, `Invoke-Expression`, `eval()`, `exec()`, `Function()`, `pickle.loads()`, `marshal.loads()`, `yaml.load()` (without `SafeLoader`), or `torch.load()` without `weights_only=True` = `🔴 CRITICAL`.
- **Subprocess Shell Injection**: `subprocess.run(..., shell=True)` or `os.system()` interpolating unsanitized arguments = `🟡 WARNING` (or `🔴 CRITICAL` if externally controlled).
- **Persistence & Rule Tampering**: Writing to or modifying `.agents/rules/`, `CLAUDE.md`, `.claude/`, `~/.gemini/`, `.git/hooks/`, `~/.bashrc`, `~/.zshrc`, `$PROFILE`, `crontab`, or Windows Scheduled Tasks (`schtasks`) = `🔴 CRITICAL`.
- **Destructive Filesystem / Git Operations**: Unscoped `rm -rf`, `Remove-Item -Recurse -Force`, `git push --force`, `git reset --hard`, or symlink/path traversal (`..` or symlinks resolving outside the skill folder) = `🔴 CRITICAL`.

---

## SC-07 — Supply Chain & Auxiliary File Hygiene (OWASP LLM03:2025)

Risks in dependencies, external CLIs (e.g., Hugging Face, npm, PyPI), binaries, and uninspected Level-3 files ([RESEARCH.md §2.5, §3](RESEARCH.md)).

- **Unpinned / Untrusted Runtime Installs**: `pip install`, `uv run`, `npm install`, `npx`, `pnpm dlx` pulling unpinned packages, typosquatted names, or direct git URLs (`git+https://...`) without version/hash pinning = `🟡 WARNING` (or `🔴 CRITICAL` if non-standard registry/URL).
- **Opaque Binaries & Archives**: Bundled `.exe`, `.dll`, `.so`, `.dylib`, `.bin`, `.pyc`, `.wasm`, `.zip`, `.tar.gz`, `.pkl`, `.pt`, `.safetensors`, `.gguf` inside a skill folder = `🔴 CRITICAL` (executables/pickles) or `🟡 WARNING` (archives/weights).
- **Uninspected Level-3 Surface (Pasted Prompt Mode)**: When auditing a prompt pasted in chat, any relative reference to `scripts/*`, `references/*`, `assets/*`, or `.mcp.json` whose content was NOT pasted by the user = `🟡 WARNING` (*"Uninspected Level-3 file: must be inspected before installation"*).

