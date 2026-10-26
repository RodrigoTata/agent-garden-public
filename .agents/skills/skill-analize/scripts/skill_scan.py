#!/usr/bin/env python3
"""Deterministic static security scanner for Agent Skills (SKILL.md + auxiliary files or pasted prompts).

Read-only tool for the `skill-analize` skill. Scans either:
  1. A local skill directory or file (`python skill_scan.py <path>`)
  2. A skill prompt pasted in chat (`python skill_scan.py --text-file <scratch.md>` or `--stdin`)

Checks SC-01 through SC-07 (see ../SECURITY-CHECKS.md and ../RESEARCH.md):
  SC-01: Concealment, Steganography & Unicode Smuggling (Tag block, Bidi, Zero-width, HTML comments, Base64/Hex)
  SC-02: Pre-Invocation RCE & Frontmatter Privilege Escalation (!`cmd`, ```!, hooks, allowed-tools, .mcp.json)
  SC-03: Level-1 Metadata Poisoning & Trigger Squatting (description / when_to_use injection & spec rules)
  SC-04: Direct & Indirect Prompt Injection (override directives, stealth instructions, sandbox bypass, mutable URLs)
  SC-05: Credential Harvesting & Data Exfiltration (sensitive paths, env dumps, outbound POST/webhooks, MD images)
  SC-06: Arbitrary Code Execution, Destructive Actions & Persistence (pipe-to-shell, eval/exec/pickle, rule tampering)
  SC-07: Supply Chain & Auxiliary File Hygiene (unpinned pip/npm/npx/uv, opaque binaries, uninspected Level-3 files)
"""

import argparse
import base64
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
SEVERITY_ICON = {"CRITICAL": "🔴 CRITICAL", "WARNING": "🟡 WARNING", "INFO": "🔵 INFO"}

CATEGORIES = {
    "SC-01": "Concealment, Steganography & Unicode Smuggling",
    "SC-02": "Pre-Invocation RCE & Frontmatter Privilege Escalation",
    "SC-03": "Level-1 Metadata Poisoning & Trigger Squatting",
    "SC-04": "Direct & Indirect Prompt Injection (OWASP LLM01)",
    "SC-05": "Credential Harvesting & Data Exfiltration (OWASP LLM06)",
    "SC-06": "Arbitrary Code Execution, Destructive Actions & Persistence",
    "SC-07": "Supply Chain & Auxiliary File Hygiene (OWASP LLM03)",
}

BINARY_CRITICAL_EXTS = {".exe", ".dll", ".so", ".dylib", ".bin", ".scr", ".bat", ".cmd", ".ps1", ".vbs", ".pkl", ".pickle", ".marshal"}
BINARY_WARNING_EXTS = {".pyc", ".pyo", ".wasm", ".zip", ".tar", ".gz", ".tgz", ".7z", ".rar", ".whl", ".pt", ".pth", ".onnx", ".gguf", ".safetensors"}
TEXT_EXTS = {
    ".md", ".txt", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx",
    ".sh", ".bash", ".zsh", ".json", ".yaml", ".yml", ".toml", ".ini",
    ".cfg", ".html", ".css", ".sql", ".r", ".rb", ".go", ".rs", ".java",
}

STANDARD_FM_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_FM_KEYS = {
    "when_to_use", "argument-hint", "arguments", "disable-model-invocation",
    "user-invocable", "disallowed-tools", "model", "effort", "context",
    "agent", "background", "hooks", "paths", "shell",
}

BIDI_CHARS = {
    0x202A: "LRE (Left-to-Right Embedding)",
    0x202B: "RLE (Right-to-Left Embedding)",
    0x202C: "PDF (Pop Directional Formatting)",
    0x202D: "LRO (Left-to-Right Override)",
    0x202E: "RLO (Right-to-Left Override)",
    0x2066: "LRI (Left-to-Right Isolate)",
    0x2067: "RLI (Right-to-Left Isolate)",
    0x2068: "FSI (First Strong Isolate)",
    0x2069: "PDI (Pop Directional Isolate)",
    0x061C: "ALM (Arabic Letter Mark)",
    0x200E: "LRM (Left-to-Right Mark)",
    0x200F: "RLM (Right-to-Left Mark)",
}

ZERO_WIDTH_CHARS = {
    0x200B: "ZWSP (Zero Width Space)",
    0x200C: "ZWNJ (Zero Width Non-Joiner)",
    0x200D: "ZWJ (Zero Width Joiner)",
    0x2060: "WJ (Word Joiner)",
    0xFEFF: "ZWNBSP / Mid-file BOM",
}


class Finding:
    def __init__(self, category: str, severity: str, file: str, line: int, title: str, detail: str, snippet: str = ""):
        self.category = category
        self.severity = severity
        self.file = file
        self.line = line
        self.title = title
        self.detail = detail
        self.snippet = snippet.strip()[:160]

    def to_dict(self):
        return {
            "category": self.category,
            "severity": self.severity,
            "file": self.file,
            "line": self.line,
            "title": self.title,
            "detail": self.detail,
            "snippet": self.snippet,
        }


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, str]], str, int]:
    """Return (frontmatter_dict, body, body_start_line)."""
    norm = text.replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n?", norm, re.S)
    if not m:
        return None, norm, 1
    fm_block = m.group(1)
    body_start_line = fm_block.count("\n") + 3
    fm: Dict[str, str] = {}
    current_key = None
    for line in fm_block.splitlines():
        kv = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if kv:
            current_key = kv.group(1)
            val = kv.group(2).strip()
            fm[current_key] = "" if val in (">-", ">", "|", "|-") else val.strip("'\"")
        elif current_key and line.startswith((" ", "\t")):
            fm[current_key] = (fm[current_key] + " " + line.strip()).strip()
    return fm, norm[m.end():], body_start_line


def scan_unicode_smuggling(text: str, rel_path: str, findings: List[Finding]) -> None:
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        # 1. Plane 14 Unicode Tag characters (U+E0000 - U+E007F)
        tag_chars = [ch for ch in line if 0xE0000 <= ord(ch) <= 0xE007F]
        if tag_chars:
            decoded = "".join(chr(ord(c) - 0xE0000) for c in tag_chars if 0xE0020 <= ord(c) <= 0xE007E)
            findings.append(Finding(
                "SC-01", "CRITICAL", rel_path, idx,
                "Unicode Tag Block Smuggling (U+E0000..U+E007F)",
                f"Found {len(tag_chars)} invisible tag character(s). Decoded hidden ASCII: {decoded!r}",
                line,
            ))

        # 2. Bidirectional control characters (Trojan Source)
        bidi_found = [f"U+{ord(ch):04X} ({BIDI_CHARS[ord(ch)]})" for ch in line if ord(ch) in BIDI_CHARS]
        if bidi_found:
            findings.append(Finding(
                "SC-01", "CRITICAL", rel_path, idx,
                "Bidirectional Control Character (Trojan Source)",
                f"Visual text reordering character(s) detected: {', '.join(sorted(set(bidi_found)))}",
                line,
            ))

        # 3. Zero-width & Variation Selectors
        zw_found = []
        for pos, ch in enumerate(line):
            cp = ord(ch)
            if cp in ZERO_WIDTH_CHARS and not (idx == 1 and pos == 0 and cp == 0xFEFF):
                zw_found.append(f"U+{cp:04X} ({ZERO_WIDTH_CHARS[cp]})")
            elif 0xFE00 <= cp <= 0xFE0F or 0xE0100 <= cp <= 0xE01EF:
                zw_found.append(f"U+{cp:04X} (Variation Selector)")
        if zw_found:
            sev = "CRITICAL" if len(zw_found) >= 3 else "WARNING"
            findings.append(Finding(
                "SC-01", sev, rel_path, idx,
                "Invisible Zero-Width / Variation Selector Characters",
                f"Found {len(zw_found)} invisible char(s) ({', '.join(sorted(set(zw_found)))}) that can split keywords or smuggle payloads.",
                line,
            ))


def scan_comments_and_encodings(text: str, rel_path: str, findings: List[Finding]) -> None:
    lines = text.splitlines()
    # HTML comments in Markdown (ignoring inline-code literals like `<!-- -->`)
    if rel_path.endswith(".md"):
        text_no_inline_code = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group(0)), text)
        for m in re.finditer(r"<!--(.*?)-->", text_no_inline_code, re.S):
            comment_body = m.group(1).strip()
            line_no = text[:m.start()].count("\n") + 1
            # Ignore standard benign slide separator used in AgentGarden carousels
            if comment_body.lower() in ("slide", "more", "toc"):
                continue
            suspicious = re.search(
                r"\b(ignore|disregard|system|prompt|curl|wget|http|bash|sh|exec|eval|secret|token|env|ssh|override|instruc)\b",
                comment_body, re.I
            )
            sev = "CRITICAL" if suspicious else "WARNING"
            findings.append(Finding(
                "SC-01", sev, rel_path, line_no,
                "Hidden HTML Comment in Markdown",
                "HTML comments are invisible in rendered GitHub/Hugging Face previews but read by the LLM.",
                comment_body.replace("\n", " "),
            ))

        # Markdown invisible reference comments: [//]: # (...)
        for idx, line in enumerate(lines, start=1):
            if re.search(r"^\s*\[//\]:\s*#\s*\(", line):
                findings.append(Finding(
                    "SC-01", "WARNING", rel_path, idx,
                    "Hidden Markdown Reference Comment",
                    "Invisible [//]: # comment detected; verify it does not conceal prompt instructions.",
                    line,
                ))

    # Base64 / Hex / Encoded payloads across all files
    for idx, line in enumerate(lines, start=1):
        # Skip standard data:image/svg+xml or shields.io badges
        if "img.shields.io" in line or "data:image/" in line:
            continue
        for b64_match in re.finditer(r"(?<![A-Za-z0-9+/=])([A-Za-z0-9+/]{44,}={0,2})(?![A-Za-z0-9+/=])", line):
            candidate = b64_match.group(1)
            # Ignore long URL paths or hashes without mixed case/digits
            if "/" in candidate and candidate.count("/") > 3:
                continue
            try:
                raw_dec = base64.b64decode(candidate, validate=True)
                printable_ratio = sum(32 <= b <= 126 or b in (9, 10, 13) for b in raw_dec) / max(len(raw_dec), 1)
                if printable_ratio > 0.85 and len(raw_dec) >= 24:
                    dec_str = raw_dec.decode("utf-8", errors="replace")
                    findings.append(Finding(
                        "SC-01", "CRITICAL", rel_path, idx,
                        "Embedded Base64-Encoded Text Payload",
                        f"Decoded Base64 string ({len(raw_dec)} bytes): {dec_str[:100]!r}",
                        line,
                    ))
            except Exception:
                pass

        if re.search(r"(\bbase64\s+(-d|--decode)\b|\bFromBase64String\b|-(?:e|enc|EncodedCommand)\s+[A-Za-z0-9+/=]{16,}|\bcodecs\.decode\s*\(.*rot_?13)", line, re.I):
            findings.append(Finding(
                "SC-01", "CRITICAL", rel_path, idx,
                "Runtime Payload Decoding Execution",
                "Decodes base64/encoded strings at runtime (classic obfuscation vector).",
                line,
            ))


def scan_skill_frontmatter_and_preexec(text: str, rel_path: str, expected_name: Optional[str], findings: List[Finding]) -> Optional[Dict[str, str]]:
    fm, body, _ = parse_frontmatter(text)
    if fm is None:
        findings.append(Finding(
            "SC-03", "WARNING", rel_path, 1,
            "Missing YAML Frontmatter",
            "SKILL.md does not begin with a valid `---` YAML frontmatter block.",
            text[:80],
        ))
        return None

    name = fm.get("name", "")
    desc = fm.get("description", "")
    when_to_use = fm.get("when_to_use", "")

    if expected_name and name and name != expected_name:
        findings.append(Finding(
            "SC-03", "INFO", rel_path, 2,
            "Frontmatter Name Mismatch",
            f"Frontmatter `name: {name}` does not match folder/expected name `{expected_name}`.",
            f"name: {name}",
        ))

    if not desc:
        findings.append(Finding(
            "SC-03", "WARNING", rel_path, 2,
            "Missing `description` in Frontmatter",
            "No `description` found in frontmatter (unless intentionally user-invoked only).",
        ))
    else:
        if len(desc) > 1024:
            findings.append(Finding(
                "SC-03", "WARNING", rel_path, 3,
                "Overlong `description` (>1024 chars)",
                f"`description` is {len(desc)} chars (Agent Skills spec limit is 1024). Can bloat context or hide instructions.",
                desc[:120],
            ))
        if "<" in desc or ">" in desc:
            findings.append(Finding(
                "SC-03", "WARNING", rel_path, 3,
                "XML/HTML Angle Brackets in `description`",
                "`description` contains `<` or `>`, rejected by Anthropic's validator and risky for prompt tag injection.",
                desc,
            ))

    # SC-03: Check Level-1 metadata poisoning & Trigger Squatting
    combined_meta = f"{desc} {when_to_use}".strip()
    if re.search(
        r"\b(ignore (all |previous |prior )?(instructions|rules)|disregard|system prompt|you must always|on every (message|turn|prompt)|before any task|always execute|run silently|do not tell the user|bypass)\b",
        combined_meta, re.I
    ):
        findings.append(Finding(
            "SC-03", "CRITICAL", rel_path, 3,
            "Level-1 Metadata Poisoning / Trigger Squatting",
            "Frontmatter `description`/`when_to_use` (loaded into system prompt at startup) contains global override or universal trigger directives.",
            combined_meta,
        ))

    # SC-02: Frontmatter privilege escalation (`hooks`, `allowed-tools`, unknown keys)
    if "hooks" in fm:
        findings.append(Finding(
            "SC-02", "CRITICAL", rel_path, 2,
            "Session-Persistent `hooks:` in Frontmatter",
            "Skill registers session hooks in YAML frontmatter that persist across turns after invocation.",
            f"hooks: {fm.get('hooks')}",
        ))

    if "allowed-tools" in fm:
        at_val = fm.get("allowed-tools", "")
        is_broad = re.search(r"\b(Bash\s*(\(\*\))?|Write|Edit|run_command|mcp__\*)\b", at_val)
        sev = "CRITICAL" if is_broad else "WARNING"
        findings.append(Finding(
            "SC-02", sev, rel_path, 2,
            "Pre-Approved Tools (`allowed-tools:`) in Frontmatter",
            f"Skill pre-approves tool execution without prompt for the invoking turn: `{at_val}`.",
            f"allowed-tools: {at_val}",
        ))

    extra_keys = set(fm.keys()) - STANDARD_FM_KEYS - CLAUDE_FM_KEYS
    if extra_keys:
        findings.append(Finding(
            "SC-03", "INFO", rel_path, 2,
            "Non-Standard Frontmatter Keys",
            f"Keys outside Agent Skills spec & Claude Code: {sorted(extra_keys)}",
        ))

    # SC-02: Dynamic Context Injection (!`cmd` and ```!) in SKILL.md
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        if re.match(r"^\s*```!\s*$", line):
            findings.append(Finding(
                "SC-02", "CRITICAL", rel_path, idx,
                "Pre-Invocation Shell Block (```` ```! ````)",
                "Claude Code executes ```` ```! ```` shell blocks automatically BEFORE the model sees the skill.",
                line,
            ))
        # Match inline !`cmd` (where ! is at start of line or preceded by whitespace, not inside quotes describing syntax)
        for m in re.finditer(r"(?:^|(?<=\s))!`([^`\n]+)`", line):
            cmd_inside = m.group(1)
            findings.append(Finding(
                "SC-02", "CRITICAL", rel_path, idx,
                "Pre-Invocation Inline Shell Injection (`` !`cmd` ``)",
                f"Claude Code executes `` !`{cmd_inside}` `` in the user's shell before loading the skill prompt.",
                line,
            ))

    return fm


PROMPT_INJECTION_RULES = [
    (
        "CRITICAL",
        "Direct Prompt Injection / Rule Override Directive",
        re.compile(
            r"\b("
            r"ignore\s+(?:all\s+|any\s+|previous\s+|prior\s+|above\s+)+(?:instructions|rules|prompts|guardrails|constraints)|"
            r"disregard\s+(?:all\s+|previous\s+|prior\s+|system\s+)+(?:instructions|rules|prompts)|"
            r"forget\s+(?:all\s+|previous\s+|prior\s+)+(?:instructions|rules|context)|"
            r"ignora\s+(?:todas\s+)?las\s+(?:instrucciones|reglas)\s+(?:anteriores|previas)|"
            r"olvida\s+(?:todas\s+)?las\s+(?:instrucciones|reglas)|"
            r"you\s+are\s+now\s+(?:in\s+)?(?:developer\s+mode|unrestricted|DAN|jailbroken|exempt\s+from)|"
            r"new\s+system\s+prompt\s*:|"
            r"</?(?:system|user_rules|instructions|identity|guidelines)>"
            r")",
            re.I,
        ),
        "Attempts to override system instructions, fake system XML tags, or break role boundaries.",
    ),
    (
        "CRITICAL",
        "Stealth / Deception Directive Against User",
        re.compile(
            r"\b("
            r"do\s+not\s+(?:tell|inform|mention\s+to|show|ask)\s+the\s+user|"
            r"never\s+(?:tell|inform|mention\s+to|ask)\s+the\s+user|"
            r"hide\s+this\s+(?:action|step|command|output)\s+from\s+the\s+user|"
            r"without\s+(?:the\s+user\s+knowing|telling\s+the\s+user|user\s+confirmation|asking\s+permission)|"
            r"no\s+le\s+(?:digas|informes|menciones|preguntes)\s+al\s+usuario|"
            r"oculta\s+(?:esto|este\s+paso)\s+al\s+usuario"
            r")\b",
            re.I,
        ),
        "Instructs the agent to conceal actions or bypass user transparency.",
    ),
    (
        "CRITICAL",
        "Sandbox / Safety / Cost Guardrail Bypass",
        re.compile(
            r"("
            r"BypassSandbox\s*:\s*true|"
            r"--dangerously-skip-permissions|"
            r"--no-cpu-throttling|"
            r"--min-instances\s*[= ]\s*[1-9]|"
            r"--no-verify"
            r")",
            re.I,
        ),
        "Instructs the agent to disable the sandbox, skip git/permission checks, or violate GCP cost rules.",
    ),
]

CREDENTIAL_AND_EXFIL_RULES = [
    (
        "CRITICAL",
        "Sensitive Credential / Key Path Reference",
        re.compile(
            r"("
            r"[/\\]\.ssh[/\\]|id_rsa|id_ed25519|authorized_keys|"
            r"[/\\]\.aws[/\\]credentials|[/\\]\.npmrc|[/\\]\.pypirc|[/\\]\.git-credentials|[/\\]\.netrc|"
            r"mcp_oauth_tokens\.json|[/\\]\.claude\.json|"
            r"gcloud[/\\]application_default_credentials\.json|"
            r"(?:cat|type|Get-Content|read_file|view_file|grep|send|post|upload|curl|wget)\b[^\n]{0,80}\.env\b"
            r")",
            re.I,
        ),
        "References private SSH keys, cloud credential stores, OAuth token files, or reads `.env` secrets.",
    ),
    (
        "CRITICAL",
        "Suspicious Exfiltration Endpoint / Webhook",
        re.compile(
            r"("
            r"webhook\.site|requestbin|pipedream\.net|ngrok-free\.app|ngrok\.io|oastify\.com|burpcollaborator|"
            r"interact\.sh|canarytokens\.com|discord(?:app)?\.com/api/webhooks|api\.telegram\.org/bot|"
            r"transfer\.sh|0x0\.st|pastebin\.com|"
            r"https?://(?!127\.|0\.0\.0\.0)(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?"
            r")",
            re.I,
        ),
        "Communicates with known exfiltration relays, webhook sinks, or raw external IP addresses.",
    ),
    (
        "CRITICAL",
        "Outbound Network Data Exfiltration Pattern",
        re.compile(
            r"("
            r"\bcurl\b[^\n]*\s(?:-d|--data|--data-binary|--data-urlencode|-F|--form|--upload-file|-T)\s|"
            r"\bwget\b[^\n]*\s--post-(?:data|file)|"
            r"\bInvoke-(?:RestMethod|WebRequest)\b[^\n]*-Method\s+Post[^\n]*-Body|"
            r"\b(?:nslookup|dig|host)\b[^\n]*\$\("
            r")",
            re.I,
        ),
        "Sends local data outbound via HTTP POST/upload or DNS command substitution.",
    ),
    (
        "CRITICAL",
        "Markdown Image Exfiltration Pattern",
        re.compile(
            r"!\[[^\]]*\]\(https?://[^)\s]*(?:\$\{|\$[A-Za-z_]|token=|secret=|key=|data=|env=)",
            re.I,
        ),
        "Dynamic external Markdown image URL with variable/query interpolation (renders in chat UI to leak context).",
    ),
    (
        "WARNING",
        "Environment Variable Dump / Access",
        re.compile(
            r"("
            r"\b(?:printenv|Get-ChildItem\s+Env:)\b|"
            r"\bos\.environ\b(?!\.get\s*\(\s*['\"](?:PATH|HOME|USERPROFILE|TEMP|TMP|TERM|CI|NODE_ENV|PYTHONPATH)['\"])|"
            r"\bprocess\.env\b(?!\.(?:NODE_ENV|PATH|HOME|CI))"
            r")",
        ),
        "Accesses or dumps environment variables; verify it only reads expected, non-secret configuration.",
    ),
]

CODE_EXEC_AND_PERSISTENCE_RULES = [
    (
        "CRITICAL",
        "Remote Pipe-to-Shell Execution",
        re.compile(
            r"("
            r"\b(?:curl|wget)\b[^\n|]*\|\s*(?:sudo\s+)?(?:ba)?sh\b|"
            r"\b(?:curl|wget)\b[^\n|]*\|\s*python\d?\b|"
            r"\b(?:iwr|irm|Invoke-WebRequest|Invoke-RestMethod)\b[^\n|]*\|\s*(?:iex|Invoke-Expression)\b"
            r")",
            re.I,
        ),
        "Downloads and pipes remote content directly into a shell interpreter.",
    ),
    (
        "CRITICAL",
        "Unsafe Dynamic Code Evaluation / Deserialization",
        re.compile(
            r"("
            r"(?<![\.\w])(?:eval|exec)\s*\(|"
            r"\bInvoke-Expression\b|"
            r"\bpickle\.loads?\s*\(|"
            r"\bmarshal\.loads?\s*\(|"
            r"\byaml\.load\s*\([^)]*(?!SafeLoader)|"
            r"\btorch\.load\s*\([^)]*(?!weights_only\s*=\s*True)"
            r")",
        ),
        "Executes dynamic strings or unsafe deserialization (`eval`, `exec`, `pickle`, unsafe `yaml.load`/`torch.load`).",
    ),
    (
        "CRITICAL",
        "Persistence / Agent Rule / Hook Tampering",
        re.compile(
            r"("
            r"[/\\]\.git[/\\]hooks[/\\]|"
            r"[/\\]\.(?:bashrc|bash_profile|zshrc|profile)\b|"
            r"\bcrontab\b|\bschtasks\b|"
            r"(?:>>|>|write_file|edit_file|Set-Content|Add-Content)[^\n]*(?:\.agents[/\\]rules|CLAUDE\.md|\.gemini[/\\]config[/\\]rules)"
            r")",
            re.I,
        ),
        "Modifies git hooks, shell startup profiles, scheduled tasks, or agent guardrail rules.",
    ),
    (
        "CRITICAL",
        "Destructive Filesystem / Git Command",
        re.compile(
            r"("
            r"\brm\s+-[rRf]{2,}\s+(?:[/~*]|\\\w|\.\.)|"
            r"\bRemove-Item\b[^\n]*-Recurse[^\n]*-Force|"
            r"\bgit\s+push\b[^\n]*--force(?!-with-lease)|"
            r"\bgit\s+reset\s+--hard\b|"
            r"\bchmod\s+(?:777|\+s)\b"
            r")",
        ),
        "Performs destructive deletion, forced history overwrite, or unsafe permission changes.",
    ),
    (
        "WARNING",
        "Subprocess / Shell Execution in Script",
        re.compile(
            r"("
            r"\bsubprocess\.(?:run|Popen|call|check_output|check_call)\s*\([^\n]*shell\s*=\s*True|"
            r"\bos\.system\s*\(|"
            r"\bchild_process\.(?:exec|execSync)\s*\("
            r")",
        ),
        "Uses shell=True or os.system/child_process.exec; verify no unsanitized input reaches the command string.",
    ),
]

SUPPLY_CHAIN_AND_FETCH_RULES = [
    (
        "WARNING",
        "Runtime Package Installation / Remote Execution (`SC-07`)",
        re.compile(
            r"("
            r"\bpip3?\s+install\b|"
            r"\buv\s+(?:pip\s+install|run\s+--with|tool\s+run)\b|"
            r"\buvx\s+|"
            r"\bnpm\s+(?:install|i)\b|"
            r"\bnpx\s+(?:-[yY]\s+)?[a-zA-Z0-9@_/-]+|"
            r"\bpnpm\s+(?:add|dlx)\b|"
            r"\bgit\s+clone\b"
            r")",
        ),
        "Installs or executes external packages/repos at runtime; verify package authenticity and version pinning.",
    ),
    (
        "WARNING",
        "External URL Fetch / Potential Indirect Prompt Injection Sink (`SC-04`)",
        re.compile(
            r"("
            r"\b(?:curl|wget|Invoke-WebRequest|Invoke-RestMethod|requests\.(?:get|post)|urllib\.request\.urlopen|fetch)\b[^\n]*https?://|"
            r"https?://(?:raw\.githubusercontent\.com|gist\.githubusercontent\.com|huggingface\.co/[^\s)\"']+)"
            r")",
            re.I,
        ),
        "Fetches remote content; ensure remote responses are treated strictly as untrusted data, never executable instructions.",
    ),
]


def scan_lines_against_rules(text: str, rel_path: str, findings: List[Finding]) -> None:
    lines = text.splitlines()
    for idx, line in enumerate(lines, start=1):
        for sev, title, pattern, detail in PROMPT_INJECTION_RULES:
            if pattern.search(line):
                findings.append(Finding("SC-04", sev, rel_path, idx, title, detail, line))
        for sev, title, pattern, detail in CREDENTIAL_AND_EXFIL_RULES:
            if pattern.search(line):
                findings.append(Finding("SC-05", sev, rel_path, idx, title, detail, line))
        for sev, title, pattern, detail in CODE_EXEC_AND_PERSISTENCE_RULES:
            if pattern.search(line):
                findings.append(Finding("SC-06", sev, rel_path, idx, title, detail, line))
        for sev, title, pattern, detail in SUPPLY_CHAIN_AND_FETCH_RULES:
            if pattern.search(line):
                cat = "SC-07" if "SC-07" in title else "SC-04"
                findings.append(Finding(cat, sev, rel_path, idx, title, detail, line))


def extract_referenced_files(md_text: str) -> List[Tuple[int, str]]:
    """Extract relative file paths referenced via Markdown links or script invocations."""
    refs: List[Tuple[int, str]] = []
    lines = md_text.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Markdown links: [label](path)
        for m in re.finditer(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", line):
            target = m.group(1).strip()
            if not re.match(r"^(?:https?|mailto|file|conversation|javascript):", target, re.I):
                refs.append((idx, target))
        # Script / file mentions in code/prose: scripts/foo.py, references/bar.md, assets/baz
        for m in re.finditer(r"(?<![A-Za-z0-9_./\\-])((?:scripts|references|assets|resources|examples)/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*)", line):
            candidate_ref = m.group(1).strip("`.,:;()[]\"'")
            if "." in Path(candidate_ref).name:
                refs.append((idx, candidate_ref))
    # Deduplicate preserving first line seen
    seen = set()
    unique_refs = []
    for line_no, target in refs:
        if target not in seen:
            seen.add(target)
            unique_refs.append((line_no, target))
    return unique_refs


def scan_mcp_config(text: str, rel_path: str, findings: List[Finding]) -> None:
    findings.append(Finding(
        "SC-02", "WARNING", rel_path, 1,
        "Bundled MCP / Plugin Configuration File",
        "Skill bundles an MCP or plugin configuration. Inspect every server command and URL for tool poisoning or arbitrary stdio execution.",
        text[:140].replace("\n", " "),
    ))
    try:
        data = json.loads(text)
        servers = data.get("mcpServers", data.get("servers", data))
        if isinstance(servers, dict):
            for srv_name, srv_cfg in servers.items():
                if isinstance(srv_cfg, dict):
                    cmd = srv_cfg.get("command", "")
                    args = " ".join(str(a) for a in srv_cfg.get("args", []))
                    url = srv_cfg.get("url") or srv_cfg.get("serverUrl") or srv_cfg.get("httpUrl") or ""
                    if cmd:
                        findings.append(Finding(
                            "SC-02", "CRITICAL", rel_path, 1,
                            f"Bundled MCP Stdio Process (`{srv_name}`)",
                            f"Spawns local command `{cmd} {args}`. Verify binary source and arguments.",
                            f"{srv_name}: {cmd} {args}",
                        ))
                    if url:
                        findings.append(Finding(
                            "SC-02", "CRITICAL", rel_path, 1,
                            f"Bundled Remote MCP Endpoint (`{srv_name}`)",
                            f"Connects to remote MCP server `{url}`. Susceptible to remote Tool Poisoning & rug pulls.",
                            f"{srv_name}: {url}",
                        ))
    except Exception:
        pass


def scan_directory(root_path: Path) -> dict:
    findings: List[Finding] = []
    scanned_files: List[dict] = []
    referenced_files: List[dict] = []

    if root_path.is_file():
        skill_root = root_path.parent
        files_to_scan = [root_path]
        expected_name = skill_root.name if root_path.name == "SKILL.md" else None
    else:
        skill_root = root_path.resolve()
        expected_name = skill_root.name
        files_to_scan = sorted(skill_root.rglob("*"))

    skill_md_text: Optional[str] = None
    frontmatter_meta: Optional[Dict[str, str]] = None

    for item in files_to_scan:
        try:
            rel_path = item.relative_to(skill_root).as_posix() if item != root_path else item.name
        except ValueError:
            rel_path = str(item)

        # Check symlink / junction escape (SC-06)
        try:
            resolved = item.resolve()
            if not root_path.is_file() and not str(resolved).startswith(str(skill_root)):
                findings.append(Finding(
                    "SC-06", "CRITICAL", rel_path, 1,
                    "Symlink / Path Traversal Escape Outside Skill Folder",
                    f"`{rel_path}` resolves outside the skill root to `{resolved}`.",
                    str(resolved),
                ))
                continue
        except Exception as exc:
            findings.append(Finding(
                "SC-06", "WARNING", rel_path, 1,
                "Unresolvable Path / Broken Symlink",
                f"Could not resolve `{rel_path}`: {exc}",
            ))
            continue

        if item.is_dir():
            continue

        ext = item.suffix.lower()
        size = item.stat().st_size

        # Check opaque binaries / archives (SC-07)
        if ext in BINARY_CRITICAL_EXTS:
            findings.append(Finding(
                "SC-07", "CRITICAL", rel_path, 1,
                f"Dangerous Executable / Deserialization Artifact (`{ext}`)",
                f"Bundled binary/serialized payload `{rel_path}` ({size} bytes) cannot be trusted statically.",
                rel_path,
            ))
            scanned_files.append({"file": rel_path, "type": "binary-critical", "bytes": size, "lines": 0})
            continue
        elif ext in BINARY_WARNING_EXTS:
            findings.append(Finding(
                "SC-07", "WARNING", rel_path, 1,
                f"Opaque Binary / Archive / Model Artifact (`{ext}`)",
                f"Bundled binary or archive `{rel_path}` ({size} bytes) requires manual provenance check.",
                rel_path,
            ))
            scanned_files.append({"file": rel_path, "type": "binary-warning", "bytes": size, "lines": 0})
            continue

        # Read text file
        raw = item.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf") and item.name == "SKILL.md":
            findings.append(Finding(
                "SC-03", "INFO", rel_path, 1,
                "UTF-8 BOM in SKILL.md",
                "SKILL.md starts with a UTF-8 BOM (`EF BB BF`); save as UTF-8 without BOM for dual-agent compatibility.",
            ))

        # Detect unexpected binary content in unknown extensions
        if b"\x00" in raw[:4096]:
            findings.append(Finding(
                "SC-07", "WARNING", rel_path, 1,
                "Binary File With Non-Standard Extension",
                f"File `{rel_path}` ({size} bytes) contains null bytes and cannot be audited as plain text.",
            ))
            scanned_files.append({"file": rel_path, "type": "binary-null", "bytes": size, "lines": 0})
            continue

        text = raw.decode("utf-8", errors="replace")
        line_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        scanned_files.append({"file": rel_path, "type": "text", "bytes": size, "lines": line_count})

        # Run checks
        scan_unicode_smuggling(text, rel_path, findings)
        scan_comments_and_encodings(text, rel_path, findings)

        if item.name == "SKILL.md":
            skill_md_text = text
            frontmatter_meta = scan_skill_frontmatter_and_preexec(text, rel_path, expected_name, findings)

        if item.name in (".mcp.json", "mcp_config.json", "plugin.json"):
            scan_mcp_config(text, rel_path, findings)

        scan_lines_against_rules(text, rel_path, findings)

    # Check referenced files from SKILL.md
    if skill_md_text is not None:
        for line_no, ref_target in extract_referenced_files(skill_md_text):
            norm_ref = Path(ref_target)
            if ".." in norm_ref.parts:
                findings.append(Finding(
                    "SC-06", "CRITICAL", "SKILL.md", line_no,
                    "Parent Directory Traversal (`..`) in Referenced Path",
                    f"`SKILL.md` references `{ref_target}` which traverses outside the skill directory.",
                    ref_target,
                ))
                referenced_files.append({"path": ref_target, "line": line_no, "status": "TRAVERSAL_ESCAPE"})
                continue

            candidate_path = (skill_root / norm_ref).resolve()
            exists = candidate_path.exists()
            if not str(candidate_path).startswith(str(skill_root.resolve())):
                findings.append(Finding(
                    "SC-06", "CRITICAL", "SKILL.md", line_no,
                    "Referenced Path Escapes Skill Root",
                    f"`{ref_target}` resolves outside `{skill_root}`.",
                    ref_target,
                ))
                referenced_files.append({"path": ref_target, "line": line_no, "status": "ESCAPE"})
            elif not exists:
                findings.append(Finding(
                    "SC-07", "WARNING", "SKILL.md", line_no,
                    "Missing / Broken Auxiliary File Reference",
                    f"`SKILL.md` references `{ref_target}` (line {line_no}), but the file does not exist in the bundle.",
                    ref_target,
                ))
                referenced_files.append({"path": ref_target, "line": line_no, "status": "MISSING"})
            else:
                referenced_files.append({"path": ref_target, "line": line_no, "status": "PRESENT_AND_SCANNED"})

    return build_report("LOCAL_BUNDLE", str(root_path), frontmatter_meta, scanned_files, referenced_files, findings)


def scan_pasted_text(text: str, source_label: str, expected_name: Optional[str]) -> dict:
    findings: List[Finding] = []
    line_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
    scanned_files = [{"file": source_label, "type": "pasted-prompt", "bytes": len(text.encode("utf-8")), "lines": line_count}]
    referenced_files: List[dict] = []

    scan_unicode_smuggling(text, source_label, findings)
    scan_comments_and_encodings(text, source_label, findings)
    frontmatter_meta = scan_skill_frontmatter_and_preexec(text, source_label, expected_name, findings)
    scan_lines_against_rules(text, source_label, findings)

    for line_no, ref_target in extract_referenced_files(text):
        if ".." in Path(ref_target).parts:
            findings.append(Finding(
                "SC-06", "CRITICAL", source_label, line_no,
                "Parent Directory Traversal (`..`) in Referenced Path",
                f"Pasted skill references `{ref_target}` which traverses outside the skill root.",
                ref_target,
            ))
            referenced_files.append({"path": ref_target, "line": line_no, "status": "TRAVERSAL_ESCAPE"})
        else:
            findings.append(Finding(
                "SC-07", "WARNING", source_label, line_no,
                "Uninspected Level-3 Auxiliary File in Pasted Prompt",
                f"Pasted skill references `{ref_target}` (line {line_no}). Request its content in chat before approving installation.",
                ref_target,
            ))
            referenced_files.append({"path": ref_target, "line": line_no, "status": "UNINSPECTED_IN_CHAT"})

    return build_report("PASTED_PROMPT", source_label, frontmatter_meta, scanned_files, referenced_files, findings)


def build_report(
    mode: str,
    target: str,
    frontmatter_meta: Optional[Dict[str, str]],
    scanned_files: List[dict],
    referenced_files: List[dict],
    findings: List[Finding],
) -> dict:
    findings.sort(key=lambda f: (SEVERITY_ORDER.get(f.severity, 99), f.category, f.file, f.line))
    counts = {"CRITICAL": 0, "WARNING": 0, "INFO": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    checklist = {}
    for cat_id, cat_name in CATEGORIES.items():
        cat_findings = [f for f in findings if f.category == cat_id]
        if not cat_findings:
            checklist[cat_id] = {"name": cat_name, "status": "CLEARED (static)", "highest_severity": "NONE", "count": 0}
        else:
            top_sev = min((f.severity for f in cat_findings), key=lambda s: SEVERITY_ORDER[s])
            checklist[cat_id] = {"name": cat_name, "status": f"FLAGGED ({top_sev})", "highest_severity": top_sev, "count": len(cat_findings)}

    if counts["CRITICAL"] > 0:
        verdict = "BLOCK — DO NOT INSTALL (CRITICAL FINDINGS)"
    elif counts["WARNING"] > 0:
        verdict = "CONDITIONAL / REVIEW REQUIRED (WARNINGS PRESENT)"
    else:
        verdict = "STATIC PASS — PROCEED TO SEMANTIC AUDIT"

    return {
        "mode": mode,
        "target": target,
        "frontmatter": frontmatter_meta or {},
        "verdict": verdict,
        "counts": counts,
        "scanned_files": scanned_files,
        "referenced_files": referenced_files,
        "checklist": checklist,
        "findings": [f.to_dict() for f in findings],
    }


def print_human_report(report: dict) -> None:
    print("=" * 78)
    print(f"SKILL-ANALIZE STATIC SECURITY REPORT ({report['mode']})")
    print("=" * 78)
    print(f"Target       : {report['target']}")
    fm = report.get("frontmatter") or {}
    if fm:
        print(f"Skill Name   : {fm.get('name', '<missing>')}")
        desc_preview = fm.get("description", "<missing>")
        print(f"Description  : {desc_preview[:110]}{'...' if len(desc_preview) > 110 else ''}")
    c = report["counts"]
    print(f"Summary      : 🔴 CRITICAL: {c['CRITICAL']}  |  🟡 WARNING: {c['WARNING']}  |  🔵 INFO: {c['INFO']}")
    print(f"Static Gate  : {report['verdict']}")
    print("-" * 78)

    print("\n1. INVENTORY OF SCANNED ARTIFACTS")
    for sf in report["scanned_files"]:
        print(f"   - {sf['file']} ({sf['type']}, {sf['lines']} lines, {sf['bytes']} bytes)")

    if report["referenced_files"]:
        print("\n2. LEVEL-3 AUXILIARY FILE REFERENCES IN SKILL.MD")
        for rf in report["referenced_files"]:
            print(f"   - line {rf['line']:>3}: {rf['path']} -> [{rf['status']}]")
    else:
        print("\n2. LEVEL-3 AUXILIARY FILE REFERENCES IN SKILL.MD")
        print("   - None detected (self-contained SKILL.md)")

    print("\n3. SECURITY CHECKLIST MATRIX (SC-01 .. SC-07)")
    for cat_id, info in report["checklist"].items():
        print(f"   - {cat_id} ({info['name']}): {info['status']} [{info['count']} finding(s)]")

    print("\n4. DETAILED FINDINGS")
    if not report["findings"]:
        print("   ✅ Zero static findings across SC-01..SC-07.")
    else:
        for idx, f in enumerate(report["findings"], start=1):
            icon = SEVERITY_ICON.get(f["severity"], f["severity"])
            print(f"\n   [{idx}] {icon} | {f['category']} | {f['file']}:{f['line']} — {f['title']}")
            print(f"       Why    : {f['detail']}")
            if f["snippet"]:
                print(f"       Snippet: {f['snippet']}")
    print("=" * 78)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic static security scanner for Agent Skills (local bundle or pasted chat prompt)."
    )
    parser.add_argument("path", nargs="?", help="Path to local skill folder or SKILL.md file (Branch A).")
    parser.add_argument("--text-file", help="Path to a temporary file containing a pasted skill prompt from chat (Branch B).")
    parser.add_argument("--stdin", action="store_true", help="Read pasted skill prompt from standard input (Branch B).")
    parser.add_argument("--name", help="Expected skill name for frontmatter check.")
    parser.add_argument("--json", action="store_true", help="Output report as JSON.")
    args = parser.parse_args()

    if args.stdin:
        content = sys.stdin.read()
        report = scan_pasted_text(content, "<pasted-chat-prompt>", args.name)
    elif args.text_file:
        tf = Path(args.text_file)
        if not tf.exists():
            sys.exit(f"ERROR: --text-file not found: {tf}")
        content = tf.read_text(encoding="utf-8", errors="replace")
        report = scan_pasted_text(content, f"<pasted:{tf.name}>", args.name)
    elif args.path:
        target = Path(args.path)
        if not target.exists():
            sys.exit(f"ERROR: Target path does not exist: {target}")
        report = scan_directory(target)
    else:
        parser.print_help()
        sys.exit(2)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_human_report(report)

    if report["counts"]["CRITICAL"] > 0:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
