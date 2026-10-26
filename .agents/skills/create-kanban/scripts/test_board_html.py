"""The Kanban board exists as Markdown (source of truth) and as a generated HTML page.

Copied into the repo as tests/test_board_html.py by the create-kanban skill. Catches the drifts
a reviewer misses: BOARD.html left stale, an item file whose `status` disagrees with its
column, a card linking to a missing file, and the user guide losing its link to the board.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_board import DEFAULT_BOARD, config, frontmatter, parse_board, render_html  # noqa: E402

BOARD_MD = DEFAULT_BOARD
BOARD_HTML = BOARD_MD.with_suffix(".html")
GUIDE_HTML = None  # e.g. ROOT / "docs" / "user-guide.html" when the repo has a user guide


def _markdown() -> str:
    return BOARD_MD.read_text(encoding="utf-8")


def test_board_html_is_regenerated_from_board_md():
    assert BOARD_HTML.exists(), "run: python scripts/render_board.py"
    assert BOARD_HTML.read_text(encoding="utf-8") == render_html(_markdown(), BOARD_MD), (
        "BOARD.html is stale: run python scripts/render_board.py"
    )


def test_every_item_file_is_on_the_board_in_the_column_its_status_names():
    prefix = config(_markdown()).get("prefix", "REQ")
    columns, _ = parse_board(_markdown(), BOARD_MD.parent)
    on_board = {card.id: col.status for col in columns for card in col.cards}
    in_files = {}
    for path in BOARD_MD.parent.glob(f"{prefix}-[0-9]*.md"):
        ident = re.match(rf"({prefix}-\d+)", path.name).group(1)
        in_files[ident] = frontmatter(path).get("status", "")

    assert on_board == in_files


def test_every_card_links_to_an_existing_file():
    columns, _ = parse_board(_markdown(), BOARD_MD.parent)
    missing = [c.href for col in columns for c in col.cards if c.href and not (BOARD_MD.parent / c.href).exists()]

    assert missing == []


def test_markdown_in_cells_is_escaped():
    board = "## 🔥 NEEDS-GRILLING\n\n| ID | Title | Type | Priority | Area |\n|---|---|---|---|---|\n" \
            "| [X-1](X-1.md) | Use <script> & `code` | bug | P0 | core |\n"

    html = render_html(board, BOARD_MD)

    assert "Use &lt;script&gt; &amp; <code>code</code>" in html and "<script> &" not in html


def test_the_user_guide_and_the_board_link_to_each_other():
    if GUIDE_HTML is None:
        return
    board_href = BOARD_HTML.relative_to(GUIDE_HTML.parent).as_posix()
    assert f'href="{board_href}"' in GUIDE_HTML.read_text(encoding="utf-8")
    assert config(_markdown()).get("guide"), 'set guide="…" in the <!-- kanban: --> line of BOARD.md'
