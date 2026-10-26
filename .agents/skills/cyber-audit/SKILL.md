---
name: cyber-audit
description: Relentless full-stack security audit of the codebase.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Cyber-Audit (Security Auditor)

Adopt the posture of a **relentless** external penetration tester. Assume every input is hostile, every guard is missing until proven present, and every "it works" is a vulnerability you haven't found yet.

> [!IMPORTANT]
> **Analyze and report only.** Do not modify code unless explicitly requested. Assume all client-side validation can be bypassed.

---

## Process

### Step 1 — Scope & Reconnaissance

Establish the attack surface before auditing anything.

1. Run `git diff --name-only` to identify changed files. These are the **primary targets**.
2. Map every exposed endpoint: controllers, public routes, unguarded paths.
3. Read `CONTEXT.md` (if present) to understand the domain model and trust boundaries.

**Completion criterion**: A written inventory of every endpoint and route in the workspace, grouped by access level (public, authenticated, admin-only).

---

### Step 2 — Relentless Sweep

Walk **every** item in [SECURITY-CHECKS.md](SECURITY-CHECKS.md) against the scoped attack surface. Do not sample — audit exhaustively. Changed files first, then widen to adjacent modules.

For each check, either:
- **Flag it** with severity (`🔴 CRITICAL`, `🟡 WARNING`, `🔵 INFO`), file, line, and an exploitation scenario.
- **Clear it** with evidence (the specific guard, validator, or configuration that prevents exploitation).

> [!CAUTION]
> A check left unaccounted is a failed audit. The completion criterion demands **every** item in the checklist is either flagged or explicitly cleared.

**Completion criterion**: Every item in [SECURITY-CHECKS.md](SECURITY-CHECKS.md) has been addressed — flagged with a finding or cleared with evidence. No check is left ambiguous or skipped.

---

### Step 3 — Security Report

Produce `security_audit_report.md` containing:

1. **Summary table**: Severity counts (`🔴`, `🟡`, `🔵`).
2. **Findings** (grouped by severity, highest first): Each with file:line, OWASP category, exploitation scenario, and remediation.
3. **Cleared checks**: A compact list of what passed and why.

> [!CAUTION]
> If `🔴 CRITICAL` findings exist, **stop here**. Present the report and demand they are fixed before proceeding to Step 4.

**Completion criterion**: `security_audit_report.md` is saved and presented. Zero `🔴 CRITICAL` findings remain if proceeding to Step 4.

---

### Step 4 — Human Penetration Plan

Generate `security_human_plan.md` for browser-based testing the agent cannot perform. Each scenario uses a step/action/expected-result table:

- **Access Control Bypass**: Log in as USER, navigate to admin URLs, curl admin endpoints with USER's JWT — verify 403.
- **Injection Attempts**: `<script>alert(1)</script>` in text fields, `' OR 1=1 --` in search, overflow values in numeric inputs.
- **Session Security**: Expired JWT returns 401, logout invalidates token, no sensitive data in localStorage or Network tab.

**Completion criterion**: `security_human_plan.md` is saved, containing ≥3 scenarios with step/action/expected-result tables and a sign-off checklist.

---

## Guardrails

- **Zero Trust**: If the backend doesn't check the role, it's a vulnerability — regardless of what the frontend does.
- **No sampling**: Audit every endpoint, every DTO, every route. Sampling is how vulnerabilities survive.
- **Traceability**: Every finding points to a specific file and line.
- **No browser**: Agent checks are static only. Browser penetration testing is the human's job (Step 4).
