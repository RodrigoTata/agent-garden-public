---
name: rule-creating
description: >-
  Create, edit, or delete agent guardrails (rules) for any workspace.
  Use when the user wants to add a rule, modify agent behavior permanently,
  set a constraint, enforce a convention, or mentions "rule", "guardrail",
  "always do", "never do", or "from now on".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Rule Creating — Guardrail Authoring

A **guardrail** is a permanent behavioural constraint the agent obeys on every turn. Creating one is a high-leverage, high-risk act: a well-placed guardrail prevents recurring mistakes; a sloppy one silently degrades every future conversation. Treat every guardrail as production config, not casual chat.

## Steps

### 1. Capture intent

Ask the user — or extract from context — what behaviour they want to constrain, enforce, or prohibit. Produce a one-sentence **intent statement**: _"The agent must/must-not [verb] when [condition]."_

**Completion criterion**: an intent statement the user confirms, or that is unambiguous from context.

### 2. Assess risk

Evaluate the intent against the [Risk Framework](RISK_FRAMEWORK.md). Classify as **low**, **medium**, or **high** risk.

| Risk   | Gate                                                                                              |
|--------|---------------------------------------------------------------------------------------------------|
| Low    | Proceed to drafting. Confirm with the user before writing.                                        |
| Medium | Surface concerns to the user. If any ambiguity remains, invoke `/grill-me-rg` before drafting.    |
| High   | **Mandatory** `/grill-me-rg` session. Do not draft until every concern is resolved.               |

**Completion criterion**: a risk level assigned and the appropriate gate passed — low confirmed, medium concerns resolved, high grilling complete.

### 3. Draft the guardrail

Write the rule file following the format below. Choose the correct **scope** and **location**:

- **Workspace rule** → `<workspace>/.agents/rules/<rule-name>.md` — applies to one project.
- **Global rule** → `~/.gemini/config/rules/<rule-name>.md` — applies to all projects.

Format:
```markdown
---
trigger: always_on
---

<Clear, imperative statement of the guardrail. One behaviour per rule.
 State what the agent MUST or MUST NOT do, and under what condition.>
```

Guardrail writing principles:
- **One rule, one behaviour.** Never bundle unrelated constraints.
- **Imperative voice.** _"Agent must…"_ or _"Agent must not…"_ — no passive, no hedging.
- **Condition-first when conditional.** _"When deploying to production, agent must…"_
- **Testable.** The agent must be able to tell compliance from violation on any given turn.
- **No no-ops.** If the agent already does it by default, the rule wastes context load.

**Completion criterion**: a rule file drafted, content reviewed against the five principles above — every principle satisfied.

### 4. Confirm and write

Present the drafted guardrail to the user. Explain:
- What behaviour it constrains.
- Its scope (workspace or global).
- Its risk classification and why.

Write the file only after the user explicitly approves. If they want changes, loop back to step 3.

**Completion criterion**: file written to disk after user approval.

### 5. Verify

Read the written rule file back and confirm it is syntactically correct (valid frontmatter, markdown body). Report the rule's path to the user.

**Completion criterion**: file read back successfully, path reported.
