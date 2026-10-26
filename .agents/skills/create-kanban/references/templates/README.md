# Requirements — {{PROJECT}}'s Kanban

Work on {{PROJECT}} flows through one board. Raw captures land in an **area Inbox**. Anything worth doing becomes an **item** (`{{PREFIX}}-###`): a feature, refactor, chore, bug, security fix, docs or research spike. [BOARD.md](BOARD.md) is the Kanban. [BOARD.html](BOARD.html) is its generated browser view.

## Columns

| Column | Status value | What it holds | Leaves when |
|---|---|---|---|
| 📥 **INBOX** | — | Ideas, bugs, anything, **1–3 lines**, in the Inbox of its area. **No id.** | Triage: it becomes an item (id, type, priority) or is deleted |
| 🔥 **NEEDS-GRILLING** | `needs-grilling` | Worth doing, but decisions are open | The open questions are closed (e.g. `/grill-me-rg`, `/grill-with-docs`) and the acceptance is testable |
| 📋 **READY-TO-DEV** | `ready-to-dev` | Decided and testable; ready to code (e.g. `/execute`, or `/to-tickets` → `/tdd`) | Someone starts coding |
| ⚙️ **IN-DEVELOPMENT** | `in-development` | Being coded on a branch | Merged with tests green |
| 🧪 **IN-QA** | `in-qa` | Being verified (e.g. a `/to-qa` agent report + human QA plan) | QA passed |
| ✅ **DONE** | `done` | {{DONE_DEFINITION}} | — |
| 🗑️ **DROPPED** | `dropped` | Decided not to do it; the file says why | — |

- **Shortcut:** a trivial bug or chore may go INBOX → READY-TO-DEV, with "no grilling needed" in its Notes.
- **Blocked** is a flag, not a column: `blocked-by: [...]` keeps the card where it is.
- **WIP limit:** at most **{{WIP}}** items IN-DEVELOPMENT.

## Inboxes (one per area)

`inbox/<area>.md`. Capturing is one bullet at the end of the right file:

```markdown
- 2026-01-31 · 🐞 The export button does nothing on an empty list. Seen twice.
```

Each bullet has a date, an optional kind (💡 idea · 🐞 bug · 🎛️ tuning · 🧹 chore · ❓ question), and 1–3 lines. No id, no priority. If the area is unclear, use [inbox/_unsorted.md](inbox/_unsorted.md).

**Triage** (weekly, or when an Inbox holds more than ~5 items). For each item, do one of two things:
- **Make it an item.** Take the next free id from BOARD.md and bump it. Create a file from [_TEMPLATE.md](_TEMPLATE.md) with status `needs-grilling` (or `ready-to-dev` via the shortcut). Add a board row, and **delete the bullet**.
- **Delete it**, if it isn't worth doing.

## Item fields

```yaml
---
id: {{PREFIX}}-001
title: Short imperative title
type: feature        # feature | refactor | chore | bug | security | docs | research
priority: P1         # P0 | P1 | P2 | P3
area: {{FIRST_AREA}} # see Areas
status: needs-grilling   # needs-grilling | ready-to-dev | in-development | in-qa | done | dropped
created: 2026-01-31
updated: 2026-01-31
blocked-by: []
links: []            # tickets, ADRs, PRs, releases
---
```

| Priority | Meaning |
|---|---|
| **P0** | Now: production broken, data at risk, or a security hole |
| **P1** | Next: needed for the current milestone |
| **P2** | Normal: valuable, not urgent |
| **P3** | Someday: nice to have |

## Areas (where in the repo it lands; each has an Inbox)

| Area | Covers |
|---|---|
{{AREA_ROWS}}

A new area needs a row here, an Inbox file and a row on the board, in the same commit.

## Working rules

1. **Moving a card:** change `status` and `updated` in the file, **and** move its row on the board, **and** run `python scripts/render_board.py`, all in the same commit. The same goes for adding an item or an Inbox bullet. `tests/test_board_html.py` fails if BOARD.html is stale or a `status` disagrees with its column.
2. **Branches and commits:** name the branch `{{PREFIX_LOWER}}-###-slug`, and mention the id in the commit, e.g. `feat(area): short summary ({{PREFIX}}-001)`.
3. **Never reuse an id,** and never delete an item: drop it, with a reason.
