"""Validate a skill in AgentGarden and make it visible to Claude Code.

Usage: python install_skill.py <skill-name> [--check] [--agentgarden <path to AgentGarden>]

--check validates only and creates no link: use it to audit many skills at once.

1. Validates <AgentGarden>/.agents/skills/<name>/SKILL.md against the rules in ../RESEARCH.md
   (Agent Skills standard + Claude Code + Antigravity): frontmatter, encoding, links.
2. Creates the junction ~/.claude/skills/<name> -> that folder (Windows) or a symlink elsewhere.
3. Reports whether README.md lists the skill.
Exit code 1 if validation fails; nothing is linked in that case.
"""
import os, re, subprocess, sys
from pathlib import Path

STANDARD = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CLAUDE_ONLY = {"when_to_use", "argument-hint", "arguments", "disable-model-invocation", "user-invocable",
               "disallowed-tools", "model", "effort", "context", "agent", "background", "hooks", "paths", "shell"}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
BOM, CRLF = b"\xef\xbb\xbf", b"\r\n"


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None, text
    fm, key = {}, None
    for line in m.group(1).splitlines():
        kv = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
            fm[key] = "" if val in (">-", ">", "|", "|-") else val.strip("'\"")
        elif key and line.startswith((" ", "\t")):
            fm[key] = (fm[key] + " " + line.strip()).strip()
    return fm, text[m.end():]


def validate(folder):
    errs, warns = [], []
    skill = folder / "SKILL.md"
    if not skill.exists():
        return [f"no existe {skill}"], warns
    raw = skill.read_bytes()
    if raw.startswith(BOM):
        errs.append("SKILL.md tiene BOM: guardar como UTF-8 sin BOM")
    if CRLF in raw:
        warns.append("SKILL.md tiene fines de línea CRLF: Claude Code y Antigravity lo leen, pero el empaquetador de Anthropic lo rechaza")
    text = raw.decode("utf-8-sig").replace("\r\n", "\n")
    fm, body = frontmatter(text)
    if fm is None:
        return errs + ["SKILL.md no empieza con frontmatter YAML (---)"], warns
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != folder.name:
        errs.append(f"name '{name}' no coincide con la carpeta '{folder.name}'")
    if not NAME_RE.match(name) or len(name) > 64:
        errs.append(f"name '{name}': solo minúsculas, dígitos y guiones simples, máx. 64")
    if re.search(r"claude|anthropic", name):
        errs.append("name no puede contener 'claude' ni 'anthropic'")
    if not desc:
        errs.append("falta description")
    elif len(desc) > 1024:
        errs.append(f"description tiene {len(desc)} caracteres (máx. 1024)")
    elif re.search(r"[<>]", desc):
        errs.append("description no puede contener '<' ni '>'")
    elif not re.search(r"\b(Use when|Úsala cuando|Usar cuando)\b", desc, re.I) and fm.get("disable-model-invocation") != "true":
        warns.append("description sin disparadores ('Use when …'): el agente no sabrá cuándo invocarla")
    extra = set(fm) - STANDARD - CLAUDE_ONLY
    if extra:
        warns.append(f"claves de frontmatter fuera del estándar: {sorted(extra)} (Claude Code las ignora; claude.ai las rechaza)")
    if set(fm) & CLAUDE_ONLY:
        warns.append(f"claves solo de Claude Code: {sorted(set(fm) & CLAUDE_ONLY)} (Antigravity no las documenta)")
    if re.search(r"\$ARGUMENTS|\$\{CLAUDE_SKILL_DIR\}|!`", body):
        warns.append("usa $ARGUMENTS / ${CLAUDE_SKILL_DIR} / !`cmd`: Antigravity los verá como texto literal")
    lines = body.count("\n")
    if lines > 500:
        warns.append(f"SKILL.md tiene {lines} líneas: mover referencia a archivos enlazados")
    for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", body):
        if re.search(r"[./]", target) and not re.match(r"^[a-z]+://", target) and not (folder / target).exists():
            errs.append(f"enlace roto: {target}")
    if re.search(r"[A-Z]:[\\/]Users[\\/]|/Users/", body):
        warns.append("ruta absoluta de usuario en SKILL.md: preferir rutas relativas a la skill")
    return errs, warns


def link(folder, name):
    dst = Path.home() / ".claude" / "skills" / name
    if dst.exists() or dst.is_symlink():
        target = Path(os.path.realpath(dst))
        return f"ya enlazada: {dst} -> {target}" + ("" if target == folder.resolve() else "  (¡apunta a otra carpeta!)")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        subprocess.check_call(["cmd", "/c", "mklink", "/J", str(dst), str(folder)], stdout=subprocess.DEVNULL)
    else:
        dst.symlink_to(folder, target_is_directory=True)
    return f"enlazada: {dst} -> {folder}"


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    name = sys.argv[1]
    root = Path(sys.argv[sys.argv.index("--agentgarden") + 1]) if "--agentgarden" in sys.argv else Path(__file__).resolve().parents[4]
    folder = root / ".agents" / "skills" / name
    errs, warns = validate(folder)
    for w in warns:
        print("AVISO ", w)
    for e in errs:
        print("ERROR ", e)
    if errs:
        sys.exit(1)
    print("OK    validación")
    if "--check" in sys.argv:
        return
    print("OK    " + link(folder, name))
    readme = root / "README.md"
    listed = readme.exists() and f"**{name}**" in readme.read_text(encoding="utf-8")
    print(("OK    " if listed else "FALTA ") + f"fila en {readme.name} (tabla 'Habilidades Disponibles')")


if __name__ == "__main__":
    main()
