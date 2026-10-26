---
name: implementation-plan
description: Design a de-risked implementation plan or blueprint before execution through non-destructive discovery, architectural seams, verification design, and mandatory user approval gate. Use when the user asks to plan, says "plan de implementación", "implementation plan", "planifica", "diseña el plan", or before tackling complex tasks.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Implementation Plan

Design an actionable, de-risked technical or operational **blueprint** before executing any changes. This skill enforces disciplined discovery, makes architectural **seams** explicit, and establishes a mandatory review **gate** to prevent premature execution and unexpected side-effects.

The plan is designed to be iterated: it can be stress-tested with `/grill-me-rg` or `/grill-with-docs`, and once approved, handed off directly to `/execute` for autonomous coding and deployment.

---

## Process

### Step 1 — Discovery (Non-Destructive Legwork)

Investigate the context using read-only operations. Do not mutate source code, databases, or environment state.

1. Inspect active files, schema definitions, database records, endpoints, or operational procedures relevant to the task.
2. Identify the root cause or operational driver with concrete technical evidence rather than assumptions.
3. Trace dependency boundaries: determine what systems are affected (e.g., frontend-only, backend API, database migrations, legal compliance, or physical logistics).

*Completion criterion*: Root cause and affected components are verified against active code or live data, with zero mutating changes made to the workspace.

---

### Step 2 — Architecture & Seams

Design the solution and establish clear **seams** separating modified components from untouched ones.

1. Define the scope of work: what must be done and, equally important, what will explicitly remain untouched.
2. Identify architectural trade-offs, security implications, or breaking changes.
3. Enumerate all files, models, or operational packages requiring changes using explicit markers:
   - `[MODIFY]`: Existing files or procedures being updated.
   - `[NEW]`: New files, entities, or assets being introduced.
   - `[DELETE]`: Deprecated files or steps being removed.
4. For non-code tasks, define explicit operational work packages, inputs, outputs, and responsible roles.

*Completion criterion*: Every required change is accounted for under an explicit seam marker, and all trade-offs or decision points are identified.

---

### Step 3 — Verification & Quality Design

Design the criteria that will prove the implementation succeeded before writing code.

1. Specify automated verification commands (e.g., test suites, typecheck, linting, build bundling).
2. Outline concrete human acceptance test cases (step-by-step smoke tests, boundary conditions, and visual checks).
3. Define rollback or fallback contingencies if the task involves high-risk migrations.

*Completion criterion*: Concrete executable test commands and step-by-step human acceptance scenarios are documented.

---

### Step 4 — Plan Publication (`implementation_plan.md`)

Publish the structured plan as an artifact for user inspection using [`TEMPLATE.md`](TEMPLATE.md).

1. Write or update the artifact at `<appDataDir>\brain\<conversation-id>/implementation_plan.md`.
2. Set artifact metadata:
   - `UserFacing`: `true`
   - `RequestFeedback`: `true`
3. Document open questions or design choices as plain text with options and recommendations (avoid closed modal buttons).

*Completion criterion*: The `implementation_plan.md` artifact is saved with complete metadata and clickable file links.

---

### Step 5 — Mandatory Review Gate & Next Steps Handoff

**STOP.** Do not start implementing or touching source files. Present the plan to the user and outline the available paths:

1. **Iterate & Refine**: If the user provides adjustments in chat, update the plan directly.
2. **Stress-Test / Grill**:
   - `/grill-me-rg`: Interview the user relentlessly to resolve trade-offs branch-by-branch.
   - `/grill-with-docs`: Run a grilling session that simultaneously captures decisions as ADRs and domain glossary entries.
3. **Execute**:
   - For code tasks: Invoke `/execute` to autonomously drive the plan through ticket breakdown (`to-tickets`), test-driven implementation (`tdd`), automated quality verification (`to-qa`), and bitácora logging.
   - For non-code tasks: Proceed with step-by-step execution upon user confirmation.

*Completion criterion*: Turn ends without code modifications, leaving the decision to the user.
