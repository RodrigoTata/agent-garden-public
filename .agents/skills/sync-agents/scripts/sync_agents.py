#!/usr/bin/env python3
"""Synchronize AgentGarden skills, rules, and multi-root VS Code workspace folders
across Google Antigravity and Claude Code on any machine.

Usage:
  python sync_agents.py [--workspace <path>] [--agentgarden <path>] [--check]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def make_dir_link(dst: Path, target: Path, check_only: bool = False) -> str:
    target_resolved = target.resolve()
    if dst.exists() or dst.is_symlink():
        try:
            current = Path(os.path.realpath(dst)).resolve()
            if current == target_resolved:
                return f"OK      {dst} -> {target_resolved}"
            return f"KEEP    {dst} (custom directory/link -> {current})"
        except OSError:
            pass
    if check_only:
        return f"MISSING {dst} -> {target_resolved}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.check_call(
            ["cmd", "/c", "mklink", "/J", str(dst), str(target_resolved)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        dst.symlink_to(target_resolved, target_is_directory=True)
    return f"LINKED  {dst} -> {target_resolved}"


def parse_code_workspace(ws_file: Path) -> list[Path]:
    raw = ws_file.read_text(encoding="utf-8-sig")
    clean = re.sub(r"//.*?$", "", raw, flags=re.M)
    clean = re.sub(r",\s*([\]}])", r"\1", clean)
    data = json.loads(clean)
    folders = []
    for entry in data.get("folders", []):
        p = entry.get("path")
        if p:
            resolved = (ws_file.parent / p).resolve()
            if resolved.exists():
                folders.append(resolved)
    return folders


def find_workspaces(target: Path) -> tuple[list[Path], list[Path]]:
    target = target.resolve()
    if target.is_file() and target.suffix == ".code-workspace":
        return [target], parse_code_workspace(target)
    ws_files = sorted(target.glob("*.code-workspace")) + sorted(target.parent.glob("*.code-workspace"))
    matched_ws = []
    folders = []
    for ws in ws_files:
        try:
            ws_folders = parse_code_workspace(ws)
        except Exception:
            continue
        if target in ws_folders or ws.parent == target:
            if ws not in matched_ws:
                matched_ws.append(ws)
            for f in ws_folders:
                if f not in folders:
                    folders.append(f)
    if target.is_dir() and target not in folders:
        folders.insert(0, target)
    return matched_ws, folders


def sync_claude_md(folder: Path, ag_root: Path, sibling_folders: list[Path], check_only: bool) -> str:
    claude_md = folder / "CLAUDE.md"
    rules_dir = folder / ".agents" / "rules"
    rule_files = sorted(rules_dir.glob("*.md")) if rules_dir.exists() else sorted((ag_root / ".agents" / "rules").glob("*.md"))
    imports = [f"@.agents/rules/{r.name}" for r in rule_files]

    others = [f for f in sibling_folders if f != folder] if folder.resolve() != ag_root else []
    ws_section = ""
    if others:
        lines = ["## Carpetas del Workspace (Multi-Root VS Code)"]
        for o in others:
            rel = os.path.relpath(o, folder).replace("\\", "/")
            lines.append(f"- `{o.name}`: `{rel}` (`{o}`)")
        ws_section = "\n".join(lines) + "\n"

    if not claude_md.exists():
        if check_only:
            return f"MISSING {claude_md}"
        content = [
            "# Claude Code — reglas del proyecto",
            "",
            "La fuente de verdad de las reglas es `.agents/rules/` (compartida con Antigravity y otros agentes).",
            "Edita las reglas allí; este archivo solo las importa. No dupliques reglas aquí.",
            "",
            "Notas para Claude Code:",
            "- Menciones a herramientas de otros agentes (`list_dir`, `view_file`, `grep_search`, `ask_question`) equivalen a Glob/Read/Grep/AskUserQuestion.",
            "- El conteo de tokens en contexto lo muestra la status line; no lo reportes al final de cada respuesta.",
            "",
        ]
        if ws_section:
            content.append(ws_section.rstrip())
            content.append("")
        content.extend(imports)
        claude_md.write_text("\n".join(content).rstrip() + "\n", encoding="utf-8", newline="\n")
        return f"CREATED {claude_md}"

    existing = claude_md.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    missing_imports = [imp for imp in imports if imp not in existing]
    needs_ws = bool(ws_section) and "Carpetas del Workspace" not in existing
    if not missing_imports and not needs_ws:
        return f"OK      {claude_md}"
    if check_only:
        return f"UPDATE  {claude_md} (missing imports/workspace section)"
    updated = existing.rstrip()
    if needs_ws:
        updated += "\n\n" + ws_section.rstrip()
    if missing_imports:
        updated += "\n" + "\n".join(missing_imports)
    claude_md.write_text(updated + "\n", encoding="utf-8", newline="\n")
    return f"UPDATED {claude_md}"


def ensure_gitignore(folder: Path, check_only: bool) -> str:
    gi = folder / ".gitignore"
    if not gi.exists() or folder.name.lower() == "agentgarden":
        return f"SKIP    {gi}"
    text = gi.read_text(encoding="utf-8-sig").replace("\r\n", "\n")
    needed = []
    for entry in (".agents/", ".claude/"):
        if not re.search(rf"(?m)^/?{re.escape(entry.rstrip('/'))}/?\s*$", text):
            needed.append(entry)
    if not needed:
        return f"OK      {gi} (.agents/ and .claude/ ignored)"
    if check_only:
        return f"UPDATE  {gi} (needs {', '.join(needed)})"
    block = "\n# Agent junctions\n" + "\n".join(needed) + "\n"
    gi.write_text(text.rstrip() + "\n" + block, encoding="utf-8", newline="\n")
    return f"UPDATED {gi}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workspace", default=".", help="Path to .code-workspace file or project directory")
    ap.add_argument("--agentgarden", default=None, help="Path to AgentGarden root")
    ap.add_argument("--check", action="store_true", help="Audit only without modifying disk")
    args = ap.parse_args()

    script_path = Path(__file__).resolve()
    ag_root = Path(args.agentgarden).resolve() if args.agentgarden else script_path.parents[4]
    ag_skills = ag_root / ".agents" / "skills"
    ag_rules = ag_root / ".agents" / "rules"
    if not ag_skills.is_dir():
        sys.exit(f"ERROR: AgentGarden skills directory not found at {ag_skills}")

    home = Path.home()
    print(f"=== AgentGarden Root: {ag_root} ===")

    # 1. Global Antigravity skills link
    agy_global_skills = home / ".gemini" / "config" / "skills"
    print(make_dir_link(agy_global_skills, ag_skills, args.check))

    # 2. Global Claude Code per-skill links + AgentGarden .claude/skills junction
    print(make_dir_link(ag_root / ".claude" / "skills", ag_skills, args.check))
    claude_global_dir = home / ".claude" / "skills"
    skill_dirs = sorted(d for d in ag_skills.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    linked_count = 0
    missing_count = 0
    for sd in skill_dirs:
        res = make_dir_link(claude_global_dir / sd.name, sd, args.check)
        if res.startswith("LINKED"):
            linked_count += 1
        elif res.startswith("MISSING"):
            missing_count += 1
    print(f"OK      ~/.claude/skills: {len(skill_dirs)} total ({linked_count} newly linked, {missing_count} missing)")

    # 3. Workspace folders discovery & linking
    ws_files, folders = find_workspaces(Path(args.workspace))
    if ws_files:
        print(f"=== VS Code Workspaces: {', '.join(w.name for w in ws_files)} ===")
    for folder in folders:
        print(f"\n--- Folder: {folder} ---")
        if folder.resolve() != ag_root:
            print(make_dir_link(folder / ".agents" / "skills", ag_skills, args.check))
            print(make_dir_link(folder / ".agents" / "rules", ag_rules, args.check))
            print(make_dir_link(folder / ".claude" / "skills", ag_skills, args.check))
            print(ensure_gitignore(folder, args.check))
        print(sync_claude_md(folder, ag_root, folders, args.check))


if __name__ == "__main__":
    main()

