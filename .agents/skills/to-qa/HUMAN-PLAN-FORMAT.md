# Human QA Plan Format

This document defines the expected structure for `qa_human_plan.md`.

```markdown
# 🧪 Human QA Plan — [Feature Name]

**Generated**: YYYY-MM-DD
**Prerequisites**: Backend running (`npm run start:local`), Frontend running (`npm run start`)
**Test User**: [specific user account or role needed]

## Context

Brief summary of what was built, linking to the PRD and TDD task.

## What the Agent Already Verified

Bullet list of behaviors confirmed by automated tests and code inspection.
**The human does NOT need to re-test these.**

## Test Scenarios

### Scenario 1: [Descriptive Name]

**Goal**: What this scenario validates from the user's perspective.
**Role**: ADMIN / USER
**Preconditions**: Any setup needed (e.g., "at least one product must exist in the catalog").
**Priority**: 🔴 MUST TEST / 🟡 SHOULD TEST / 🔵 NICE TO TEST

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1    | Navigate to `/catalog` | Catalog list loads with all products |
| 2    | Click "Nuevo Item" | Product creation form opens |
| 3    | Select "Administrativo" in Tipo | Botanical fields hide |

**Edge cases to try**:
- [ ] Empty inputs on required fields
- [ ] Boundary values (e.g., extremely high prices)

### Scenario 2: ...

...

## Regression Checks

Quick smoke tests on **existing** functionality that could have been affected:

| Area | What to verify | Priority |
|------|---------------|----------|
| Dispensaciones | Creating a new reservation works | HIGH |
| PDF Receipts | Download an old receipt — format unchanged | MEDIUM |

## Sign-Off

- [ ] All scenarios passed
- [ ] All regression checks passed
- [ ] No visual regressions observed
- [ ] Overall UX is acceptable

**Tested by**: _______________
**Date**: _______________
```
