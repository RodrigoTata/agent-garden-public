---
name: context-compactor
description: Compact conversation history into a minimal checkpoint. Use when the conversation gets too long, the AI loses track, or before a heavy task.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Context Compactor

**Compact** the current conversation history into a clean, minimal checkpoint.

> [!IMPORTANT]
> **Ask the user which level to apply before compacting.** 

---

## Process

### Step 1 — Select Level

Present these compaction levels to the user and wait for their choice:

| Level | Name | What it keeps | What it removes |
|---|---|---|---|
| 1 | **Soft Clean** | All decisions, all code, all history | Long terminal outputs, failed tool calls, repeated messages |
| 2 | **Turn Summary** | Final code, key decisions | Old chat turns replaced by a 2-line summary per exchange |
| 3 | **Milestone Focus** | Completed task list, current architecture, open file paths | All conversation history |
| 4 | **Executive Summary** | One paragraph: current state + immediate next steps | Everything else |
| 5 | **Hard Reset** | Original system instructions + open file paths | All chat history, all context |

**Completion criterion**: The user has explicitly replied with their chosen compaction level.

---

### Step 2 — Generate Checkpoint

Based on the selected level, **compact** the history into a single, self-contained message that serves as the new starting point for the conversation. 

Follow the exact structure and writing rules in [CHECKPOINT-FORMAT.md](CHECKPOINT-FORMAT.md).

**Completion criterion**: A formatted Checkpoint Block matching [CHECKPOINT-FORMAT.md](CHECKPOINT-FORMAT.md) is printed to the chat.

---

### Step 3 — Activate Token Counter

From this point forward, **every response must end with a token estimate line**:

```markdown
---
**Estimated context tokens:** ~[N]
```

Estimate conservatively based on conversation length and file content loaded. This line must appear in every subsequent response, not just the one following compaction.

**Completion criterion**: The token estimate line is appended to the current response, and the rule is internalized for all future turns.

---

## Guardrails

- **Never discard open decisions silently.** If the user picks Level 4 or 5 but there are unresolved choices, flag them explicitly before compacting.
- **Never invent project state.** The checkpoint must reflect what actually exists — no speculative features.
- **Do not compact automatically.** Always wait for level selection (Step 1).
- **Do not run tools during compaction** unless the user asks you to verify a specific file path or state.
