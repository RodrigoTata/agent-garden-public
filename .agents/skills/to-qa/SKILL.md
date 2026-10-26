---
name: to-qa
description: Run automated QA checks and plan human testing. Use after completing a /tdd cycle, or when the user mentions "QA".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Post-TDD QA

Run this skill **after** a `/tdd` cycle completes (all tests GREEN). 
TDD proves the code matches the tests; **QA** proves the system matches the user's expectations.

> [!IMPORTANT]
> **No Browser.** All agent checks are static analysis and code inspection. Browser testing is exclusively the human's responsibility.

## Process

### Step 1 — Agent Sweep

Gather context from the `task.md` or PRD, then run an automated **sweep** across all modified files to catch errors before the human tests.

1. **Build & Test**:
   ```bash
   // turbo
   npm run build
   ```
   ```bash
   // turbo
   npm run test
   ```
   *Any build or test failure is `🔴 CRITICAL`.*

2. **Code Inspection**:
   - Use `grep_search` (pattern: `TODO|FIXME|HACK|XXX|console\.log`) across modified files to find leaked placeholders.
   - Audit user-facing strings (Spanish typos, capitalization consistency).
   - Verify DTO ↔ Entity ↔ Frontend Model alignment (missing fields = `🟡 WARNING`).
   - Check import integrity (no orphaned imports or circular dependencies).
   - Review business logic for edge cases (division by zero, unhandled nulls, floating point precision).

**Completion criterion**: A compiled list of findings classified by severity (`🔴 CRITICAL`, `🟡 WARNING`, `🔵 INFO`).

---

### Step 2 — Agent QA Report

Translate the **sweep** findings into a formal report.
Follow the exact markdown structure defined in [AGENT-REPORT-FORMAT.md](AGENT-REPORT-FORMAT.md).

> [!CAUTION]
> If there are any `🔴 CRITICAL` findings, **stop and fix them** immediately before proceeding to Step 3.

**Completion criterion**: `qa_agent_report.md` is saved to disk, and **zero** `🔴 CRITICAL` findings remain unfixed in the codebase.

---

### Step 3 — Human QA Plan

Generate a manual testing **plan** for the user to execute in the browser. 
Derive this from the PRD user stories and the agent findings. Do NOT include tests for things the agent or unit tests already verified.

Follow the exact markdown structure defined in [HUMAN-PLAN-FORMAT.md](HUMAN-PLAN-FORMAT.md).

**Writing Good Scenarios**:
- **Goals** must tie to a PRD user story.
- **Actions** must be concrete ("Click 'Nuevo Item'"), not vague ("use the form").
- **Expected Results** must be observable ("Fields disappear"), not internal ("state updates").
- Prioritize: `🔴 MUST TEST`, `🟡 SHOULD TEST`, `🔵 NICE TO TEST`.

**Completion criterion**: `qa_human_plan.md` is saved and presented to the user, highlighting the number of scenarios, top priorities, and areas needing extra human attention.

---

## Guardrails

- **Complementary, not redundant**: Do not ask the human to click-test basic logic that unit tests already proved.
- **Traceability**: Every agent finding must point to a specific file and line.
