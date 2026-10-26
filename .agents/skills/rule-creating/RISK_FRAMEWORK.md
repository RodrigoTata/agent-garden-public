# Risk Framework — Guardrail Creation

Disclosed reference for [`rule-creating`](SKILL.md). Use this to classify the risk of a proposed guardrail before drafting it.

## Risk Dimensions

Evaluate each dimension independently. The **highest** score across all dimensions determines the overall risk level.

### 1. Blast Radius

How many conversations and workflows does this guardrail affect?

| Score  | Criteria                                                                 |
|--------|--------------------------------------------------------------------------|
| Low    | Affects a single, narrow workflow (e.g., "format commit messages as…").  |
| Medium | Affects a category of work (e.g., "when writing tests, always…").       |
| High   | Affects all interactions (e.g., "never modify files without asking").    |

### 2. Reversibility

How easy is it to undo damage if the guardrail is wrong?

| Score  | Criteria                                                                          |
|--------|-----------------------------------------------------------------------------------|
| Low    | Trivially reversible — delete the rule file and behaviour returns to default.      |
| Medium | Reversible but costly — the rule may have caused the agent to establish patterns that persist in code, docs, or habits across conversations. |
| High   | Irreversible consequences — the rule governs destructive actions (deploy, delete, overwrite) where a wrong constraint could cause data loss or a wrong permission could allow it. |

### 3. Ambiguity

How precisely can the agent evaluate compliance?

| Score  | Criteria                                                                       |
|--------|--------------------------------------------------------------------------------|
| Low    | Binary and mechanical — the agent can always tell compliant from non-compliant.|
| Medium | Requires judgement but has clear examples — "production-quality" with examples. |
| High   | Subjective or context-dependent — "write clean code", "be careful".            |

### 4. Conflict Potential

Could this guardrail contradict existing rules or the agent's system instructions?

| Score  | Criteria                                                                    |
|--------|-----------------------------------------------------------------------------|
| Low    | No existing rules in the same domain. Independent constraint.               |
| Medium | Overlaps with an existing rule but does not contradict — may cause duplication. |
| High   | Directly contradicts an existing rule or system instruction.                |

## Risk Classification

| Overall | Condition                                      | Required Gate                         |
|---------|-------------------------------------------------|---------------------------------------|
| **Low**    | All dimensions score Low.                      | User confirmation before writing.     |
| **Medium** | Any dimension scores Medium, none scores High. | Surface concerns; `/grill-me-rg` if ambiguity remains. |
| **High**   | Any dimension scores High.                     | Mandatory `/grill-me-rg` session.     |

## Grilling Triggers

When invoking `/grill-me-rg`, focus the session on resolving:

- **Ambiguous intent**: What exactly does the user mean? Get concrete examples of compliant and non-compliant behaviour.
- **Scope creep**: Is the rule broader than the user realizes? Probe for edge cases.
- **Conflict detection**: Walk through existing rules and check for contradictions.
- **Unintended consequences**: What workflows might this rule break? What would the agent stop doing that the user currently relies on?
- **Testability**: Can the agent reliably tell if it is following the rule? If not, the rule needs sharpening.
