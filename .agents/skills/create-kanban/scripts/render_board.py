"""Render a Markdown Kanban board (BOARD.md) as a browsable, Notion-style HTML board.

Copy this file into the repo as scripts/render_board.py, then:

    python scripts/render_board.py                      # docs/requirements/BOARD.md -> BOARD.html
    python scripts/render_board.py --board path/BOARD.md
    python scripts/render_board.py --check              # exit 1 if BOARD.html is stale

BOARD.md is the source of truth; BOARD.html is generated and never edited by hand.
Per-repo settings live in BOARD.md itself, in one comment line (all keys optional):

    <!-- kanban: title="Tareas de Acme" brand="Acme" icon="🧠" lang="es" primary="#1e6ba8"
                 guide="../user-guide.html" prefix="REQ" wip="2" -->

Columns are the board's `## <emoji> <COLUMN-KEY>` headings, in order. Each column holds a
Markdown table whose first cell links the item file: `| [REQ-001](REQ-001-slug.md) | Title | ... |`.
An `INBOX` column instead lists area Inboxes: `| area | [inbox/area.md](inbox/area.md) | n |`,
whose items are bullets `- YYYY-MM-DD · <kind emoji> text`.
Standard library only.
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BOARD = ROOT / "docs" / "requirements" / "BOARD.md"

# Known column keys -> accent colour. Any other `## KEY` heading still renders, in grey.
ACCENT = {
    "INBOX": "#64748b", "BACKLOG": "#64748b", "NEEDS-GRILLING": "#ea580c", "READY-TO-DEV": "#2563eb",
    "READY": "#2563eb", "IN-DEVELOPMENT": "#7c3aed", "IN-PROGRESS": "#7c3aed", "IN-REVIEW": "#0891b2",
    "IN-QA": "#d97706", "BLOCKED": "#dc2626", "DONE": "#16a34a", "DROPPED": "#475569",
}
LABELS = {
    "es": {"item": "elemento", "items": "elementos", "next_id": "próximo id libre", "wip": "límite WIP", "all_areas": "Todas las áreas",
           "all_prio": "Toda prioridad", "search": "Buscar…", "empty": "Sin elementos", "empty_inboxes": "Inboxes vacíos",
           "guide": "Instructivo", "rules": "Reglas del tablero", "print": "Imprimir / PDF", "light": "Modo Claro",
           "dark": "Modo Noche", "board_view": "Board by Status", "table_view": "Table · Show all", "open_inbox": "Abrir el Inbox",
           "cols": ("ID", "Título", "Estado", "Tipo", "Prioridad", "Área", "Detalle"),
           "note": "Solo lectura. Se genera desde <code>{src}</code> con <code>python scripts/render_board.py</code>. "
                   "Para mover una tarjeta, edita el Markdown y el <code>status</code> del archivo en el mismo commit, y vuelve a generar.",
           "footer": "generado desde", "prio": {"P0": "P0 · Ahora", "P1": "P1 · Alta", "P2": "P2 · Normal", "P3": "P3 · Algún día"}},
    "en": {"item": "item", "items": "items", "next_id": "next free id", "wip": "WIP limit", "all_areas": "All areas",
           "all_prio": "Any priority", "search": "Search…", "empty": "No items", "empty_inboxes": "Empty inboxes",
           "guide": "User guide", "rules": "Board rules", "print": "Print / PDF", "light": "Light mode",
           "dark": "Dark mode", "board_view": "Board by Status", "table_view": "Table · Show all", "open_inbox": "Open the Inbox",
           "cols": ("ID", "Title", "Status", "Type", "Priority", "Area", "Detail"),
           "note": "Read-only. Generated from <code>{src}</code> with <code>python scripts/render_board.py</code>. "
                   "To move a card, edit the Markdown and the file's <code>status</code> in the same commit, then regenerate.",
           "footer": "generated from", "prio": {"P0": "P0 · Now", "P1": "P1 · High", "P2": "P2 · Normal", "P3": "P3 · Someday"}},
}
ACRONYMS = {"QA", "PR", "WIP", "UAT", "CI"}
PRIO_CSS = {"P0": "p0", "P1": "p1", "P2": "p2", "P3": "p3"}
KIND = {"💡": "idea", "🐞": "bug", "🎛️": "tuning", "🧹": "chore", "❓": "question"}
META_ICON = {"area": "🏷️", "mark": "🎯", "milestone": "🎯", "blocked by": "⛔", "branch": "🌿", "qa report": "🧪",
             "deployed": "🚀", "released": "🚀", "revision": "📦", "reason": "💬", "owner": "👤", "assignee": "👤"}
CORE = {"id", "title", "type", "priority"}


@dataclass
class Card:
    id: str
    href: str
    title: str
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class InboxArea:
    area: str
    href: str
    items: list[tuple[str, str, str]]


@dataclass
class Column:
    key: str
    cards: list[Card] = field(default_factory=list)
    inboxes: list[InboxArea] = field(default_factory=list)

    @property
    def label(self) -> str:
        words = self.key.replace("-", " ").capitalize().split()
        return " ".join(w.upper() if w.upper() in ACRONYMS else w for w in words)

    @property
    def status(self) -> str:
        return self.key.lower()


# --- Parsing -------------------------------------------------------------------------------------

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def config(markdown: str) -> dict[str, str]:
    m = re.search(r"<!--\s*kanban:(.*?)-->", markdown, flags=re.DOTALL)
    return dict(re.findall(r'(\w+)="([^"]*)"', m.group(1))) if m else {}


def frontmatter(path: Path) -> dict[str, str]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---", path.read_text(encoding="utf-8"), flags=re.DOTALL)
    if not m:
        return {}
    pairs = (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    return {k.strip(): v.split("#")[0].strip() for k, v in pairs}


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _link(cell: str) -> tuple[str, str]:
    m = _LINK.search(cell)
    return (m.group(1), m.group(2)) if m else (cell.strip("*"), "")


def _inbox_items(path: Path) -> list[tuple[str, str, str]]:
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- (\d{4}-\d{2}-\d{2}) · (\S+) (.+)$", line.strip())
        if m:
            items.append((m.group(1), m.group(2), m.group(3)))
    return items


def parse_board(markdown: str, board_dir: Path) -> tuple[list[Column], str]:
    columns: list[Column] = []
    current: Column | None = None
    header: list[str] = []
    next_id = ""
    for line in markdown.splitlines():
        if m := re.search(r"\*\*Next free id:\*\*\s*`([^`]+)`", line):
            next_id = m.group(1)
        if line.startswith("## "):
            m = re.search(r"(?<![\w-])([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*)(?![\w-])", line[3:])
            current = Column(m.group(1)) if m else None
            if current:
                columns.append(current)
            header = []
            continue
        if current is None or not line.startswith("|") or re.match(r"^\|[\s|:-]+\|$", line):
            continue
        cells = _cells(line)
        if not header:
            header = [h.lower() for h in cells]
            continue
        row = dict(zip(header, cells))
        if current.key == "INBOX":
            _, href = _link(row.get("inbox", ""))
            area = row.get("area", "").strip("*")
            current.inboxes.append(InboxArea(area, href, _inbox_items(board_dir / href) if href else []))
        else:
            ident, href = _link(row.get("id", cells[0]))
            fields = {k: v for k, v in row.items() if k not in ("id", "title") and v not in ("", "—", "-")}
            current.cards.append(Card(ident, href, row.get("title", ""), fields))
    return columns, next_id


# --- Rendering -----------------------------------------------------------------------------------


def _inline(text: str) -> str:
    out = escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    return _LINK.sub(lambda m: f'<a href="{escape(m.group(2), quote=True)}">{m.group(1)}</a>', out)


def _badge(css: str, label: str) -> str:
    return f'<span class="badge {css}">{escape(label)}</span>'


def _card(card: Card, t: dict) -> str:
    f = card.fields
    ptype, prio = f.get("type", ""), f.get("priority", "")
    badges = ([_badge(f"t-{re.sub(r'[^a-z]', '', ptype.lower()) or 'other'}", ptype.capitalize())] if ptype else []) + (
        [_badge(PRIO_CSS.get(prio, "p2"), t["prio"].get(prio, prio))] if prio else [])
    meta = "".join(
        f'<div class="meta-line"><span>{META_ICON.get(k, "•")}</span> {_inline(v)}</div>'
        for k, v in f.items() if k not in CORE
    )
    attrs = f'data-area="{escape(f.get("area", ""), quote=True)}" data-priority="{escape(prio, quote=True)}"'
    tag, href = ("a", f' href="{escape(card.href, quote=True)}"') if card.href else ("div", "")
    return (
        f'<{tag} class="card"{href} {attrs}><div class="card-title"><span class="card-icon">📄</span>'
        f'<span><span class="card-id">[{escape(card.id)}]</span> {_inline(card.title)}</span></div>'
        f'<div class="badges">{"".join(badges)}</div>{meta}</{tag}>'
    )


def _inbox(box: InboxArea, t: dict) -> str:
    items = "".join(
        f'<li><span title="{KIND.get(kind, "")}">{escape(kind)}</span> {_inline(text)} <span class="date">{date}</span></li>'
        for date, kind, text in box.items
    )
    return (
        f'<div class="card inbox" data-area="{escape(box.area, quote=True)}" data-priority="">'
        f'<div class="card-title"><span class="card-icon">📥</span><span>[INBOX] {escape(box.area)}</span>'
        f'<a class="inbox-link" href="{escape(box.href, quote=True)}" title="{t["open_inbox"]}">{len(box.items)}</a></div>'
        f'<ul>{items}</ul>{_badge("t-inbox", "Inbox")}</div>'
    )


def _column(col: Column, t: dict) -> str:
    color = ACCENT.get(col.key, "#64748b")
    if col.key == "INBOX":
        count = sum(len(b.items) for b in col.inboxes)
        body = "".join(_inbox(b, t) for b in col.inboxes if b.items)
        empty = [b for b in col.inboxes if not b.items]
        if empty:
            links = " ".join(f'<a href="{escape(b.href, quote=True)}">{escape(b.area)}</a>' for b in empty)
            body += f'<div class="empty-inboxes"><span>📭 {t["empty_inboxes"]}</span>{links}</div>'
    else:
        count = len(col.cards)
        body = "".join(_card(c, t) for c in col.cards)
    body = body or f'<div class="empty-col">{t["empty"]}</div>'
    return (
        f'<section class="column" style="--accent:{color}"><div class="column-head"><span class="pill">{escape(col.label)}</span>'
        f'<span class="count">{count}</span></div><div class="column-body">{body}</div></section>'
    )


def _rows(columns: list[Column]) -> str:
    rows = []
    for col in columns:
        for c in col.cards:
            f = c.fields
            detail = " · ".join(_inline(v) for k, v in f.items() if k not in CORE | {"area"})
            rows.append(
                f'<tr data-area="{escape(f.get("area", ""), quote=True)}" data-priority="{escape(f.get("priority", ""), quote=True)}">'
                f'<td>{f"<a href={chr(34)}{escape(c.href, quote=True)}{chr(34)}>{escape(c.id)}</a>" if c.href else escape(c.id)}</td>'
                f'<td>{_inline(c.title)}</td><td><span class="pill" style="--accent:{ACCENT.get(col.key, "#64748b")}">{escape(col.label)}</span></td>'
                f'<td>{escape(f.get("type", "").capitalize())}</td><td>{escape(f.get("priority", ""))}</td>'
                f'<td>{escape(f.get("area", ""))}</td><td>{detail or "—"}</td></tr>'
            )
    return "".join(rows)


def _darken(hex_color: str, factor: float = 0.85) -> str:
    h = hex_color.lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        return "#195b8f"
    return "#" + "".join(f"{int(int(h[i:i + 2], 16) * factor):02x}" for i in (0, 2, 4))


def render_html(markdown: str, board_path: Path) -> str:
    cfg = config(markdown)
    lang = cfg.get("lang", "en") if cfg.get("lang", "en") in LABELS else "en"
    t = LABELS[lang]
    columns, next_id = parse_board(markdown, board_path.parent)
    primary = cfg.get("primary", "#1e6ba8")
    brand = cfg.get("brand", "Kanban")
    guide = cfg.get("guide", "")
    total = sum(len(c.cards) for c in columns)
    areas = sorted(({c.fields.get("area", "") for col in columns for c in col.cards}
                    | {b.area for col in columns for b in col.inboxes}) - {""})
    subtitle = [f"{total} {t['item'] if total == 1 else t['items']}"]
    if next_id:
        subtitle.append(f"{t['next_id']} <code>{escape(next_id)}</code>")
    if cfg.get("wip"):
        subtitle.append(f"{t['wip']}: {escape(cfg['wip'])}")
    guide_btn = f'<a class="btn-action" href="{escape(guide, quote=True)}">📘 {t["guide"]}</a>' if guide else ""
    rules = board_path.parent / "README.md"
    rules_btn = f'<a class="btn-action" href="README.md">📐 {t["rules"]}</a>' if rules.exists() else ""
    try:
        src = board_path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        src = board_path.name
    return TEMPLATE.format(
        lang=lang, title=escape(cfg.get("title", f"{brand} · Kanban")), brand=escape(brand), icon=escape(cfg.get("icon", "🗂️")),
        primary=primary, primary_dark=_darken(primary), guide_btn=guide_btn, rules_btn=rules_btn, board_md=escape(board_path.name),
        subtitle=" · ".join(subtitle), columns="".join(_column(c, t) for c in columns), rows=_rows(columns),
        area_options="".join(f'<option value="{escape(a, quote=True)}">{escape(a)}</option>' for a in areas),
        th="".join(f"<th>{h}</th>" for h in t["cols"]), note=t["note"].format(src=escape(src)),
        footer=f'{escape(cfg.get("title", brand))} · {t["footer"]} {escape(board_path.name)}',
        **{k: t[k] for k in ("light", "dark", "print", "board_view", "table_view", "all_areas", "all_prio", "search")},
    )


TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="generator" content="scripts/render_board.py from {board_md}">
<title>{title}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
:root {{
    --bg-page: #070b14; --bg-bar: rgba(13, 20, 36, 0.94); --border: rgba(51, 65, 85, 0.65);
    --col-bg: rgba(15, 23, 42, 0.55); --card-bg: rgba(24, 34, 58, 0.92); --card-hover: rgba(36, 50, 80, 0.95);
    --text-title: #ffffff; --text-body: #cbd5e1; --text-muted: #94a3b8; --primary: {primary}; --primary-dark: {primary_dark};
    --table-row: rgba(15, 23, 42, 0.6); --table-row-alt: rgba(24, 34, 58, 0.5);
}}
body.theme-light {{
    --bg-page: #f1f5f9; --bg-bar: #ffffff; --border: #e2e8f0; --col-bg: #e9eef5; --card-bg: #ffffff; --card-hover: #f8fafc;
    --text-title: #0f172a; --text-body: #334155; --text-muted: #64748b; --table-row: #ffffff; --table-row-alt: #f8fafc;
}}
body {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg-page); color: var(--text-body); font-size: 13px; line-height: 1.5; transition: background-color .25s, color .25s; }}
a {{ color: inherit; }}
code {{ font-family: Consolas, 'JetBrains Mono', monospace; font-size: 11px; background: rgba(148,163,184,.15); padding: 1px 5px; border-radius: 4px; }}
.top-bar {{ background: var(--bg-bar); backdrop-filter: blur(14px); border-bottom: 1px solid var(--border); padding: 14px 28px; display: flex; align-items: center; justify-content: space-between; position: sticky; top: 0; z-index: 50; }}
.brand {{ display: flex; align-items: center; gap: 12px; }}
.brand-icon {{ width: 36px; height: 36px; border-radius: 10px; background: linear-gradient(135deg, var(--primary), var(--primary-dark)); display: flex; align-items: center; justify-content: center; font-size: 18px; }}
.brand-title {{ font-size: 15px; font-weight: 800; color: var(--text-title); }}
.brand-subtitle {{ font-size: 11.5px; color: var(--text-muted); }}
.top-actions {{ display: flex; gap: 10px; flex-wrap: wrap; }}
.btn-action {{ background: var(--card-bg); border: 1px solid var(--border); color: var(--text-body); font: 600 12px 'Inter', sans-serif; padding: 7px 14px; border-radius: 9px; text-decoration: none; cursor: pointer; transition: all .2s; }}
.btn-action:hover {{ transform: translateY(-1px); color: var(--text-title); }}
.btn-action.primary {{ background: var(--primary); border-color: var(--primary); color: #fff; }}
.btn-action.theme-toggle {{ background: rgba(245,158,11,.15); color: #f59e0b; border-color: rgba(245,158,11,.4); }}
.page {{ padding: 26px 28px 40px; }}
h1 {{ font-size: 28px; font-weight: 800; color: var(--text-title); letter-spacing: -.5px; }}
.subtitle {{ color: var(--text-muted); margin: 6px 0 16px; }}
.toolbar {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 16px; }}
.view-tab {{ background: none; border: none; color: var(--text-muted); font: 600 13px 'Inter', sans-serif; padding: 6px 10px; border-radius: 7px; cursor: pointer; }}
.view-tab.active {{ background: var(--card-bg); color: var(--text-title); }}
.spacer {{ flex: 1; }}
.toolbar select, .toolbar input {{ background: var(--card-bg); border: 1px solid var(--border); color: var(--text-body); border-radius: 7px; padding: 6px 9px; font: 12px 'Inter', sans-serif; }}
.board {{ display: flex; gap: 12px; overflow-x: auto; align-items: flex-start; padding-bottom: 12px; }}
.column {{ background: var(--col-bg); border-radius: 12px; min-width: 272px; max-width: 272px; padding: 10px; }}
.column-head {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }}
.pill {{ background: color-mix(in srgb, var(--accent) 28%, transparent); color: color-mix(in srgb, var(--accent) 55%, var(--text-title)); font-weight: 700; font-size: 12px; padding: 2px 8px; border-radius: 5px; white-space: nowrap; }}
.count {{ color: var(--text-muted); font-weight: 600; }}
.column-body {{ display: flex; flex-direction: column; gap: 8px; }}
.card {{ display: block; background: var(--card-bg); border: 1px solid var(--border); border-radius: 9px; padding: 10px 11px; text-decoration: none; box-shadow: 0 1px 3px rgba(0,0,0,.25); transition: background .15s, transform .15s; }}
a.card:hover {{ background: var(--card-hover); transform: translateY(-1px); }}
.card code {{ word-break: break-all; }}
.card-title {{ display: flex; gap: 7px; align-items: flex-start; color: var(--text-title); font-weight: 600; font-size: 13px; line-height: 1.4; }}
.card-icon {{ opacity: .75; }}
.card-id {{ color: var(--text-muted); font-weight: 700; }}
.badges {{ display: flex; flex-wrap: wrap; gap: 5px; margin: 8px 0 4px; }}
.badge {{ font-size: 11px; font-weight: 600; padding: 1px 7px; border-radius: 4px; display: inline-block; background: rgba(100,116,139,.3); color: #cbd5e1; }}
.t-feature {{ background: rgba(202,138,4,.25); color: #eab308; }}
.t-bug, .t-security {{ background: rgba(220,38,38,.22); color: #f87171; }}
.t-refactor, .t-tuning, .t-research, .t-spike {{ background: rgba(124,58,237,.22); color: #c4b5fd; }}
.t-docs {{ background: rgba(8,145,178,.22); color: #67e8f9; }}
.t-inbox {{ background: rgba(147,51,234,.25); color: #d8b4fe; margin-top: 8px; }}
.p0 {{ background: rgba(220,38,38,.3); color: #fecaca; }} .p1 {{ background: rgba(37,99,235,.3); color: #bfdbfe; }}
.p2 {{ background: rgba(234,88,12,.25); color: #fdba74; }} .p3 {{ background: rgba(100,116,139,.3); color: #cbd5e1; }}
body.theme-light .badge {{ color: #334155; }} body.theme-light .t-feature {{ color: #854d0e; }} body.theme-light .t-bug, body.theme-light .t-security {{ color: #b91c1c; }}
body.theme-light .t-refactor, body.theme-light .t-tuning, body.theme-light .t-research, body.theme-light .t-spike {{ color: #5b21b6; }}
body.theme-light .t-docs {{ color: #155e75; }} body.theme-light .t-inbox {{ color: #6b21a8; }}
body.theme-light .p0 {{ color: #991b1b; }} body.theme-light .p1 {{ color: #1e40af; }} body.theme-light .p2 {{ color: #9a3412; }}
.meta-line {{ color: var(--text-muted); font-size: 11.5px; margin-top: 3px; }}
.inbox ul {{ list-style: none; margin-top: 7px; display: flex; flex-direction: column; gap: 5px; }}
.inbox li {{ font-size: 12px; color: var(--text-body); }}
.inbox .date {{ color: var(--text-muted); font-size: 10.5px; }}
.inbox-link {{ margin-left: auto; min-width: 22px; text-align: center; background: rgba(148,163,184,.18); border-radius: 10px; font-size: 11px; padding: 0 6px; text-decoration: none; color: var(--text-body); }}
.empty-inboxes {{ display: flex; flex-wrap: wrap; gap: 5px; padding: 6px 2px; font-size: 11.5px; color: var(--text-muted); }}
.empty-inboxes span {{ width: 100%; font-weight: 600; }}
.empty-inboxes a {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 5px; padding: 1px 7px; text-decoration: none; color: var(--text-body); }}
.empty-col {{ color: var(--text-muted); font-style: italic; padding: 8px 4px; }}
.table-wrap {{ display: none; overflow-x: auto; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
th {{ background: var(--primary-dark); color: #fff; text-align: left; padding: 8px 10px; font-weight: 600; }}
td {{ padding: 7px 10px; border-bottom: 1px solid var(--border); background: var(--table-row); vertical-align: top; }}
tr:nth-child(even) td {{ background: var(--table-row-alt); }}
.callout {{ margin-top: 18px; border-left: 4px solid var(--primary); background: color-mix(in srgb, var(--primary) 12%, transparent); padding: 10px 14px; border-radius: 0 8px 8px 0; }}
.footer {{ margin-top: 20px; color: var(--text-muted); font-size: 11.5px; }}
body.view-table .board {{ display: none; }} body.view-table .table-wrap {{ display: block; }}
.hidden {{ display: none !important; }}
@page {{ size: A4 landscape; margin: 1cm; }}
@media print {{
    body, body.theme-light {{ background: #fff !important; color: #000 !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
    .no-print {{ display: none !important; }}
    .page {{ padding: 0; }}
    .board {{ flex-wrap: wrap; overflow: visible; }}
    .column {{ background: #f4f6f9 !important; break-inside: avoid; }}
    .card {{ background: #fff !important; border: 1px solid #ddd !important; box-shadow: none !important; break-inside: avoid; }}
    .card-title, h1 {{ color: #000 !important; }}
    .meta-line, .subtitle, .footer, .count {{ color: #444 !important; }}
    td {{ background: #fff !important; color: #111 !important; }}
}}
@media (max-width: 800px) {{ .top-bar {{ flex-direction: column; gap: 10px; align-items: flex-start; padding: 12px 16px; }} .page {{ padding: 18px 14px; }} }}
</style>
</head>
<body>
<header class="top-bar no-print">
  <div class="brand">
    <div class="brand-icon">🗂️</div>
    <div><div class="brand-title">{brand} · Kanban</div><div class="brand-subtitle">{board_md}</div></div>
  </div>
  <div class="top-actions">
    <button id="btn-theme-toggle" class="btn-action theme-toggle" onclick="toggleTheme()">☀️ {light}</button>
    {guide_btn}
    <a class="btn-action" href="{board_md}">📄 {board_md}</a>
    {rules_btn}
    <button class="btn-action primary" onclick="window.print()">🖨️ {print}</button>
  </div>
</header>
<main class="page">
  <h1>{icon} {title}</h1>
  <p class="subtitle">{subtitle}</p>
  <div class="toolbar no-print">
    <button class="view-tab active" data-view="board" onclick="setView('board')">▦ {board_view}</button>
    <button class="view-tab" data-view="table" onclick="setView('table')">☰ {table_view}</button>
    <span class="spacer"></span>
    <select id="f-area" onchange="applyFilters()"><option value="">{all_areas}</option>{area_options}</select>
    <select id="f-priority" onchange="applyFilters()"><option value="">{all_prio}</option><option>P0</option><option>P1</option><option>P2</option><option>P3</option></select>
    <input id="f-text" type="search" placeholder="🔍 {search}" oninput="applyFilters()">
  </div>
  <div class="board">{columns}</div>
  <div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>
  <div class="callout">{note}</div>
  <p class="footer">{footer}</p>
</main>
<script>
  const LABEL_LIGHT = '☀️ {light}', LABEL_DARK = '🌙 {dark}';
  function toggleTheme() {{
    const light = document.body.classList.toggle('theme-light');
    document.getElementById('btn-theme-toggle').innerHTML = light ? LABEL_DARK : LABEL_LIGHT;
    try {{ localStorage.setItem('doc-theme', light ? 'light' : 'dark'); }} catch (e) {{}}
  }}
  function setView(view) {{
    document.body.classList.toggle('view-table', view === 'table');
    document.querySelectorAll('.view-tab').forEach(b => b.classList.toggle('active', b.dataset.view === view));
    try {{ localStorage.setItem('board-view', view); }} catch (e) {{}}
  }}
  function applyFilters() {{
    const area = document.getElementById('f-area').value, prio = document.getElementById('f-priority').value;
    const text = document.getElementById('f-text').value.toLowerCase();
    document.querySelectorAll('.card, tbody tr').forEach(el => {{
      const ok = (!area || el.dataset.area === area) && (!prio || el.dataset.priority === prio) && (!text || el.textContent.toLowerCase().includes(text));
      el.classList.toggle('hidden', !ok);
    }});
  }}
  document.addEventListener('DOMContentLoaded', () => {{
    let theme = null, view = null;
    try {{ theme = localStorage.getItem('doc-theme'); view = localStorage.getItem('board-view'); }} catch (e) {{}}
    if (theme === 'light') {{ document.body.classList.add('theme-light'); document.getElementById('btn-theme-toggle').innerHTML = LABEL_DARK; }}
    if (view === 'table') setView('table');
  }});
</script>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--board", type=Path, default=DEFAULT_BOARD)
    parser.add_argument("--check", action="store_true", help="exit 1 if the HTML is stale")
    args = parser.parse_args()
    board = args.board.resolve()
    out = board.with_suffix(".html")
    html = render_html(board.read_text(encoding="utf-8"), board)
    if args.check:
        if not out.exists() or out.read_text(encoding="utf-8") != html:
            sys.exit(f"{out.name} is stale: run python scripts/render_board.py")
        print(f"{out.name} is up to date.")
        return
    out.write_text(html, encoding="utf-8", newline="\n")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
