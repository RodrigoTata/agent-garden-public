---
name: create-kanban
description: Scaffolds a repo's Kanban board (an agent-readable BOARD.md with item files, area Inboxes, rules and an agent rule) and renders it as a Notion-style HTML board kept in sync by a test. Use when the user wants a kanban, task board, backlog or tablero for a repo, wants an existing BOARD.md viewable in the browser or linked from a user guide, or when another skill needs a place to track work items.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Create Kanban

A repo's work lives on one **board**. `BOARD.md` is the **source of truth**: agents read it and edit it. `BOARD.html` is **rendered** from it by `scripts/render_board.py`, never hand-edited, and a **guard** test fails the moment the two drift.

Pick the **branch** from what the repo already has:

| Branch | When | Steps |
|---|---|---|
| **Scaffold** | No board yet | 1 → 6 |
| **Render** | A Markdown board exists, no HTML | 1, 3 → 6 (adapt the existing board to the format in Step 2's reference) |
| **Refresh** | Board and renderer exist; content changed | `python scripts/render_board.py`, then Step 6 |

## Step 1: Survey

Look for:
- an existing board (`**/BOARD.md`, `docs/requirements/`, a TODO or backlog file);
- a **user guide pair**, meaning a Markdown source plus its `/generate-html-doc` HTML (a file with `id="btn-theme-toggle"`);
- the repo's **modules** (to become areas), its language, and what "done" means there: deployed, released or merged.

Resolve the `<!-- kanban: -->` settings:

| Key | Source |
|---|---|
| `title`, `brand`, `icon` | The project name, the README's title and the guide's brand icon |
| `lang` | `es` or `en`, from the docs' language |
| `primary` | The guide's `--primary` CSS variable, so board and guide look like one product; else `#1e6ba8` |
| `guide` | The guide HTML's path relative to the board directory, or empty if there's no guide |
| `prefix`, `wip` | `REQ` and `2`, unless the repo already uses others |

**Completion criterion:** every key has a value (or is deliberately empty), and the areas list maps to real directories or modules.

## Step 2: Scaffold the board (Scaffold branch only)

Create `docs/requirements/` (or the repo's docs folder) from [references/templates/](references/templates/), filling every `{{PLACEHOLDER}}`:

| Template | Becomes |
|---|---|
| `BOARD.md` | `BOARD.md`: the config line from Step 1, one Inbox row per area plus `_unsorted`, and empty columns. `{{DONE_COLUMN}}` is whatever proves "done" here: Revision, Release or PR. |
| `README.md` | `README.md`: the board system. `{{AREA_ROWS}}` has one row per area with the paths it covers; `{{DONE_DEFINITION}}` is this repo's definition of done. |
| `_TEMPLATE.md` | `_TEMPLATE.md` |
| `inbox.md` | `inbox/<area>.md` for every area, plus `inbox/_unsorted.md` |
| `agent-rule.md` | `.agents/rules/board-workflow.md`. If the repo has a `CLAUDE.md`, import the rule there (`@.agents/rules/board-workflow.md`); otherwise create one with that line. |

Seed items **only from evidence already in the repo**: TODO/FIXME comments, an improvement log, open issues, specs. Seed nothing otherwise; an empty board is valid.

**Completion criterion:** no `{{` is left in any created file (search for it). Every area has an Inbox file and a board row, and the next free id equals one plus the highest id used.

## Step 3: Install the renderer

Copy [scripts/render_board.py](scripts/render_board.py) to the repo's `scripts/`. It needs only the standard library, and every setting comes from the board's config line. If the board isn't at `docs/requirements/BOARD.md`, change `DEFAULT_BOARD` there. Then run `python scripts/render_board.py` and `python scripts/render_board.py --check`.

**Completion criterion:** `BOARD.html` exists next to `BOARD.md`, and `--check` prints "is up to date".

## Step 4: Link the board and the user guide

When a guide exists, the two pages link to each other:
- in the guide HTML's `.top-actions`, add `<a class="btn-action" href="<path>/BOARD.html">🗂️ Tablero Kanban</a>` (or "Kanban board");
- repoint any other `BOARD.md` links **inside the HTML** to `BOARD.html`, and leave Markdown-to-Markdown links alone;
- the board's own **📘 guide** button comes from `guide=` in the config line.

If the guide's own Markdown and HTML must stay in sync (a guide-sync rule or test), follow that rule for these edits.

**Completion criterion:** each page opens the other from its top bar.

## Step 5: Guard it

Copy [scripts/test_board_html.py](scripts/test_board_html.py) to `tests/`. Set `GUIDE_HTML` if there's a guide. If the repo has no Python test runner, wire `python scripts/render_board.py --check` into CI or a pre-commit hook instead, and say so. Add the working rule "move the row, update the `status`, re-render, one commit" if the README template wasn't used.

**Completion criterion:** the tests pass. **Mutation-check:** change one item's `status` in its file, confirm a test goes red, revert.

## Step 6: See it

Screenshot the board in a headless browser and **look at it**. Edge on Windows:

```bash
"/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe" --headless=new --hide-scrollbars --window-size=1800,1000 --screenshot="$TEMP/board.png" "file:///<abs path>/BOARD.html"
```

Then check:
- [ ] Columns in board order, with correct counts; cards show id, title, type and priority badges, and meta lines.
- [ ] Only non-empty Inboxes appear as cards; the empty ones are compact links.
- [ ] Nothing overflows a card (long code wraps).
- [ ] The theme toggle, the **Board / Table** views and the area, priority and text filters work, and the print layout is landscape on white.
- [ ] The guide and board buttons link to each other (Step 4).

**Completion criterion:** every box is ticked on the screenshot, not assumed.

Report the paths (board, HTML, renderer, test, agent rule), the branch taken, and how to move a card.
