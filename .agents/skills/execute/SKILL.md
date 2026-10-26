---
name: execute
description: Executes a PRD, spec, idea or bug end-to-end autonomously through to-tickets, tdd and to-qa, or one half of that split between an architect agent and a worker agent. Use when the user asks to execute a plan, to prepare tickets for a worker agent (plan), or to have a worker build ready tickets (build).
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Execute

Drive work from a PRD, spec, idea or bug to QA'd code. This is a **relentless** workflow: it overrides the human-review gates of the skills it runs and does not stop until its mode's last step.

## Modes

The pipeline can run in one agent, or be split between an **architect** (the stronger model, which makes every design decision) and a **worker** (the cheaper model, which only executes them). The tickets are the handoff between the two.

| Mode    | Who       | Steps         | Stops after                 |
| ------- | --------- | ------------- | --------------------------- |
| `plan`  | architect | 1, 4          | Tickets published           |
| `build` | worker    | 2, 3, 4       | QA artifacts generated      |
| `full`  | one agent | 1, 2, 3, 4    | QA artifacts generated      |

Take the mode from the first argument. With no mode given: if the input is existing tickets (a `.scratch/<feature-slug>/` path or tracker reference), run `build`; otherwise run `full`.

## Process

### 1. Breakdown (`to-tickets`) — `plan`, `full`

Read the input and apply the `to-tickets` skill.
**Override**: Skip the "Quiz the user" step. Draft the slices and publish them immediately.

In `plan` mode, write **worker-ready tickets** as `to-tickets` defines them.

*Completion criterion*: Every ticket is published with its blocking edges and seams under test. In `plan` mode, additionally: every ticket passes the `to-tickets` **cold-start test**. Then skip to step 4, and end by handing the user the command for the worker: `/execute build <feature-slug or tracker reference>`.

### 2. Implementation (`tdd`) — `build`, `full`

In `build` mode, load the tickets from the given reference; without one, use the `.scratch/*/issues/` folder holding `ready-for-agent` tickets. Read every ticket before starting.

Work the frontier: for every ticket whose blockers are done, apply the `tdd` skill (red → green loop).
**Override**: The seams come from the ticket's Seams under test — do not ask. Do not ask for human feedback between tickets. When a ticket is green, set its Status to `done` and pick up the next ready ticket.

When a ticket leaves something undecided:

- **`full`** — make the best technical decision, record it in the ticket, keep moving.
- **`build`** — design belongs to the architect. Implementation details inside the ticket's decisions are yours; anything that would change a public interface, a behaviour, or the scope is not. Set the ticket's Status to `needs-architect`, append the open question to it, and move to the next ready ticket. Tickets it blocks stay blocked.

*Completion criterion*: Every ticket is `done` or `needs-architect`, and the test suite is green.

### 3. Verification (`to-qa`) — `build`, `full`

Apply the `to-qa` skill: run the automated QA checks and prepare the human testing plan. List every `needs-architect` ticket, with its question, as open work in the agent report.

*Completion criterion*: `qa_agent_report.md` and `qa_human_plan.md` exist, and zero `🔴 CRITICAL` findings remain unfixed.

### 4. Hand-off — every mode

Stop and present the outcome to the user for human review.

*Completion criterion*: The outcome is presented to the user: tests passing, QA result, or tickets handed to the worker.
