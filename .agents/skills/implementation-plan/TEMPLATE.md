# Implementation Plan: [Initiative / Task Title]

## 1. Goal & Context
Brief statement of the problem, operational need, or feature objective. Explain what occurs today vs. what is expected once completed.

## 2. Diagnostics & Discovery
Summary of the evidence gathered during read-only inspection (active endpoints, database tables, models, components, or operational workflows).
- **Current state**:
- **Root cause / Driver**:
- **Impacted systems**:

## 3. User Review Required / Critical Decisions
> [!IMPORTANT]
> Highlight breaking changes, architectural trade-offs, security implications, or business decisions requiring explicit user sign-off.

## 4. Open Questions & Alternatives
If there is ambiguity, list the questions along with recommended options and rationale (ready for review or `/grill-me-rg`):
1. **[Decision Point 1]**:
   - Option A: ...
   - Option B: ...
   - *Recommendation*: ... (explain why).

---

## 5. Proposed Changes & Seams

### Component / Module: [Name]
Demarcate exactly what changes and what remains untouched.

- `[MODIFY]` [filename](file:///absolute/path/to/file): Description of modification.
- `[NEW]` [filename](file:///absolute/path/to/file): Purpose of new file or asset.
- `[DELETE]` [filename](file:///absolute/path/to/file): Rationale for removal.

*(For non-code tasks, replace file lists with explicit operational work packages and responsibilities).*

---

## 6. Verification & Quality Plan

### Automated Checks
- Commands to run (unit tests, linters, typechecks, build bundle):
  ```bash
  [command here]
  ```

### Manual Acceptance Tests
1. **Scenario 1**: Step-by-step human verification checklist.
2. **Scenario 2**: Edge cases and error handling validation.

---

## 7. Next Steps & Handoff
- **To challenge & stress-test**: Run `/grill-me-rg` or `/grill-with-docs`.
- **To execute (code)**: Run `/execute` to drive tickets, TDD, and QA autonomously.
- **To execute (general/manual)**: Approve and proceed step-by-step.
