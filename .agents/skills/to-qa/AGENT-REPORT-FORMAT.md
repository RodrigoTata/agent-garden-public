# Agent QA Report Format

This document defines the expected structure for `qa_agent_report.md`.

```markdown
# 🔍 Agent QA Report — [Feature Name]

**Date**: YYYY-MM-DD
**TDD Cycle**: [reference to task.md or issue numbers]
**Files Scanned**: N files

## Summary

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | X |
| 🟡 WARNING  | Y |
| 🔵 INFO     | Z |

## Findings

### 🔴 Critical

1. **[Finding title]** — `file.ts:L42`
   Description of the issue and suggested fix.

### 🟡 Warning

1. ...

### 🔵 Info

1. ...

## Automated Checks Passed

- [x] Backend compiles without errors
- [x] Frontend compiles without errors (if applicable)
- [x] All tests pass
- [x] No orphaned imports or circular dependencies
- [x] DTOs and entities are aligned
```
