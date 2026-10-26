---
name: debug
description: Triage and diagnose bugs reported by non-technical users. Use when the user reports a bug, error, or unexpected behavior in plain language.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Debug (Token-Efficient Root-Cause Analysis)

**Triage** software errors reported by non-technical users quickly and cheaply. Never burn tokens exploring code until you know the **tier** of the problem.

> [!IMPORTANT]
> The user is a QA tester or end-user. Translate their plain language into technical hypotheses. **Never ask for stack traces, log files, or code details.**

---

## Process

### Step 1 — Intake & Triage (Low Token Cost)

Gather context without burning tokens, then **triage** the bug into a severity tier.

1. **User Interview**: Ask a maximum of 3 rounds of simple, concrete questions (1-2 questions max per round) in Spanish. Ask about what they saw, what they were doing, what they expected, or if they have a screenshot.
2. **Reconnaissance**: Do a quick codebase scan (e.g. `grep_search` or `git log --oneline -10`) to locate the feature. (3-5 tool calls max).
3. **Classify**: Assign exactly one tier:
   - 🟢 **T1 (Surface)**: Typo, wrong label, cosmetic. (Minimal cost)
   - 🟡 **T2 (Logic)**: Wrong output, validation error, DTO mismatch. (Moderate cost)
   - 🟠 **T3 (Structural)**: Broken feature, wiring wrong, service fails. (Significant cost)
   - 🔴 **T4 (Systemic)**: Data loss, race condition, slowness. (Full investigation)

Present the `DIAGNÓSTICO INICIAL` to the user following [REPORT-FORMATS.md](REPORT-FORMATS.md) and wait for confirmation.

**Completion criterion**: The user has confirmed or corrected your initial diagnosis and tier classification.

---

### Step 2 — Investigation (Proportional to Tier)

Investigate the root cause according to the strict token budget of the confirmed tier.

- **T1 (Surface)**: 1-3 tool calls. Go directly to the file and fix it. No report needed.
- **T2 (Logic)**: 5-10 tool calls. Apply 5 Whys. Find where the logic diverges. Output the `CAUSA ENCONTRADA (T2)` report.
- **T3 (Structural)**: 10-20 tool calls. Apply Fault Tree Analysis. Map the failure path and eliminate branches. Output the `ÁRBOL DE FALLA (T3)` report.
- **T4 (Systemic)**: Full Root-Cause Analysis. Check logs, timeline, and blast radius. Form and test hypotheses. Output the `ANÁLISIS DE CAUSA RAÍZ (T4)` report.

Follow the exact markdown structures for all reports in [REPORT-FORMATS.md](REPORT-FORMATS.md). Wait for user approval before fixing (for T3 and T4).

**Completion criterion**: The root cause is isolated, and the corresponding tier report is printed to the user.

---

### Step 3 — Fix & Verify

1. **Apply the Fix**: Make the minimum necessary changes. Preserve all unrelated logic and comments.
2. **Agent Verification**:
   - T1: Lint pass.
   - T2: Run relevant test file.
   - T3: `npm run build` + affected test suites.
   - T4: Full build + full test suite.
3. **User Verification**: Ask the user to verify the fix in plain Spanish (e.g., "¿Puedes refrescar la página y verificar que se ve bien?").

**Completion criterion**: The fix is committed to the workspace, agent verification passes, and the user is prompted to verify.

---

## Guardrails

- **Never skip triage.** Classify first, even if the fix seems obvious.
- **Respect the budget.** Never exceed the tier's tool-call budget. If a T2 reveals a T4 problem, re-classify and inform the user.
- **Fix causes, not symptoms.** Never add a null check just to silence an error without knowing why it's null.
- **Escalate, don't guess.** If the budgeted investigation yields nothing, tell the user honestly.
- **No jargon.** Never use terms like "DTO", "injection", or "middleware" when talking to the user.
