# Work flows through the Kanban board

`{{BOARD_DIR}}/BOARD.md` is the single list of what's captured, planned, in progress and done in this repo. Rules: `{{BOARD_DIR}}/README.md`.

**Before starting work:** read BOARD.md. Pick from 📋 READY-TO-DEV (highest priority first), and respect the WIP limit on ⚙️ IN-DEVELOPMENT. Don't start a 🔥 NEEDS-GRILLING item: its open questions need the user first.

**Found something along the way** (a bug, an idea, a chore) that isn't the current task? Don't fix it silently. Capture one bullet in its area Inbox (`{{BOARD_DIR}}/inbox/<area>.md`): `- YYYY-MM-DD · 🐞 text`.

**Changing an item's state:** in the same commit,
1. set `status` and `updated` in the item file;
2. move its row to the matching column in BOARD.md;
3. run `python scripts/render_board.py` (regenerates BOARD.html).

**Creating an item:** use the **Next free id** in BOARD.md and bump it. Copy `_TEMPLATE.md`, and add the board row. Never reuse or delete an id: drop it with a reason.

**Never** edit BOARD.html by hand. `tests/test_board_html.py` fails when it's stale or a `status` disagrees with the board.
