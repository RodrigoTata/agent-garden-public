"""powerautomate-dev helper: read, map, lint and debug Power Automate cloud flows.

Usage:
  python pa.py get   <flow-url | env flowId> [--out DIR]   # definition.json + map.md
  python pa.py lint  <DIR/definition.json>                  # static findings
  python pa.py runs  <flow-url | env flowId> [--top N] [--status Failed]
  python pa.py run   <flow-url | env flowId> <runId>        # per-action status, errors, repetitions
  python pa.py list  <env> [texto]                          # flows visibles para ti (propios + compartidos)

Auth: Azure CLI (`az login` once). Read-only: this script never writes to a flow.
"""
import json, os, re, subprocess, sys, urllib.request, urllib.error, urllib.parse
from collections import Counter
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AZ = os.environ.get("AZ_PATH") or (r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd" if os.name == "nt" else "az")
FLOW_API = "https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/{env}/flows/{flow}"
API_VER = "api-version=2016-11-01"
_tok = {}


def token(resource="https://service.flow.microsoft.com/"):
    if resource not in _tok:
        out = subprocess.check_output([AZ, "account", "get-access-token", "--resource", resource], text=True)
        _tok[resource] = json.loads(out)["accessToken"]
    return _tok[resource]


def http(url, auth=True):
    h = {"Authorization": "Bearer " + token()} if auth else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=h)) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {url.split('?')[0]}\n{e.read().decode()[:600]}")


def parse_target(args):
    """Accept a make.powerautomate.com URL or `env flowId`."""
    m = re.search(r"environments/([^/]+)/(?:solutions/[^/]+/)?flows/([0-9a-f-]{36})", args[0])
    if m:
        return m.group(1), m.group(2), args[1:]
    return args[0], args[1], args[2:]


def base(env, flow):
    return FLOW_API.format(env=env, flow=flow)


# ---------------------------------------------------------------- get / map
def walk(actions, depth=0, parent=None):
    """Yield (name, action, depth, parent, branch) in runAfter order."""
    order = topo(actions)
    for name in order:
        a = actions[name]
        yield name, a, depth, parent, None
        for branch, sub in children(a):
            for item in walk(sub, depth + 1, name):
                yield item[0], item[1], item[2], item[3], item[4] or branch


def children(a):
    out = []
    if a.get("actions"):
        out.append(("then" if a.get("type") == "If" else "body", a["actions"]))
    if a.get("else", {}).get("actions"):
        out.append(("else", a["else"]["actions"]))
    for case, c in (a.get("cases") or {}).items():
        out.append((f"case:{case}", c.get("actions", {})))
    if a.get("default", {}).get("actions"):
        out.append(("default", a["default"]["actions"]))
    return out


def topo(actions):
    done, order = set(), []
    def visit(n):
        if n in done or n not in actions:
            return
        done.add(n)
        for dep in (actions[n].get("runAfter") or {}):
            visit(dep)
        order.append(n)
    for n in actions:
        visit(n)
    return order


def op_of(a):
    host = (a.get("inputs") or {}).get("host") or {}
    api = (host.get("apiId") or "").split("/")[-1].replace("shared_", "")
    return f"{api}.{host.get('operationId')}" if api else a.get("type")


def cmd_get(args):
    env, flow, rest = parse_target(args)
    out = rest[rest.index("--out") + 1] if "--out" in rest else f"flow-{flow[:8]}"
    os.makedirs(out, exist_ok=True)
    f = http(f"{base(env, flow)}?{API_VER}&$expand=properties.definition,properties.connectionReferences")
    json.dump(f, open(os.path.join(out, "definition.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    p = f["properties"]
    d = p.get("definition", {})
    lines = [f"# {p.get('displayName')}", "",
             f"- state: **{p.get('state')}**  created: {p.get('createdTime')}  modified: {p.get('lastModifiedTime')}",
             f"- env: `{env}`  flow: `{flow}`",
             f"- connections: {', '.join(v.get('apiName') or k for k, v in (p.get('connectionReferences') or {}).items())}"]
    for k in ("flowSuspensionReason", "flowSuspensionTime", "flowFailureAlertSubscribed"):
        if p.get(k) is not None:
            lines.append(f"- {k}: {p[k]}")
    lines += ["", "## Trigger"]
    for k, t in d.get("triggers", {}).items():
        lines.append(f"- `{k}` {op_of(t)}" + (f"  conditions: {t['conditions']}" if t.get("conditions") else ""))
    lines += ["", "## Actions (runAfter order)"]
    for name, a, depth, parent, branch in walk(d.get("actions", {})):
        tag = f"[{branch}] " if branch and branch != "body" else ""
        ra = a.get("runAfter") or {}
        nonok = {k: v for k, v in ra.items() if v != ["Succeeded"]}
        extra = f"  runAfter≠ok: {nonok}" if nonok else ""
        if a.get("type") == "Foreach":
            extra += f"  over: {a.get('foreach')}"
        if a.get("type") == "If":
            extra += f"  if: {json.dumps(a.get('expression'), ensure_ascii=False)[:160]}"
        lines.append(f"{'  ' * depth}- {tag}`{name}` {op_of(a)}{extra}")
    open(os.path.join(out, "map.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n-> {out}/definition.json, {out}/map.md")


# ---------------------------------------------------------------- lint
DEFAULT_NAME = re.compile(r"^(For_each|Apply_to_each|Condición|Condition|Scope|Ámbito|Compose|Redactar|Switch|"
                          r"Actualizar_elemento|Update_item|Crear_elemento|Create_item|Obtener_elementos|Get_items|"
                          r"Inicializar_variable|Initialize_variable|Establecer_variable|Set_variable|HTTP)(_\d+)?$")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def cmd_lint(args):
    f = json.load(open(args[0], encoding="utf-8"))
    d = f["properties"]["definition"]
    acts = list(walk(d.get("actions", {})))
    by = {n: a for n, a, *_ in acts}
    raw = json.dumps(d, ensure_ascii=False)
    find = []

    def add(sev, rule, where, msg):
        find.append((sev, rule, where, msg))

    # error handling
    if not any(v != ["Succeeded"] for _, a, *_ in acts for v in (a.get("runAfter") or {}).values()):
        add("ALTA", "sin-manejo-errores", "flujo", "Ninguna acción corre tras Failed/TimedOut: una falla muere en silencio. Envolver en Scope Try + Scope Catch (runAfter Failed,TimedOut) que notifique.")
    for n, a, depth, parent, _ in acts:
        t, inp = a.get("type"), a.get("inputs") or {}
        params = inp.get("parameters") or {}
        op = op_of(a)
        # loops over queries
        if t == "Foreach":
            src = a.get("foreach", "")
            m = re.search(r"outputs\('([^']+)'\)", src)
            if m and m.group(1) in by and "GetItems" in op_of(by[m.group(1)]):
                add("ALTA", "loop-sobre-consulta", n, f"Itera el resultado de `{m.group(1)}`. Si se espera 1 elemento, usar first(...) y $top=1; si llegan 0 el loop no hace nada y NO avisa (pérdida silenciosa). Agregar condición length(...)=0 → alerta.")
            if depth >= 1 and parent and by.get(parent, {}).get("type") == "Foreach":
                add("MEDIA", "loop-anidado", n, "Apply to each anidado: costo O(n·m) en acciones y requests. Reemplazar el interno por Filter array / Select.")
            if any(op_of(c).endswith(("StartAndWaitForAnApproval", "CreateAnApproval")) or c.get("type") == "OpenApiConnectionWebhook"
                   for _, c, *_ in walk(a.get("actions", {}))):
                add("MEDIA", "espera-en-loop", n, "Aprobación/webhook dentro de un loop: cada iteración bloquea la ejecución (hasta 30 días). Sacarla del loop.")
            conc = ((a.get("runtimeConfiguration") or {}).get("concurrency") or {}).get("repetitions")
            if conc and conc > 1 and re.search(r"(SetVariable|AppendTo)", json.dumps(a.get("actions", {}))):
                add("ALTA", "variable-en-paralelo", n, f"Concurrencia {conc} con Set/Append variable dentro: condición de carrera. Usar Compose/Select o concurrencia 1.")
        if "GetItems" in op or "GetRows" in op or "ListRows" in op:
            if not any(k.lower().endswith(("$filter", "filter")) for k in params):
                add("ALTA", "consulta-sin-filtro", n, "Trae la tabla completa. Agregar $filter OData en el servidor.")
            if not any(k.lower().endswith(("$top", "top")) for k in params):
                add("BAJA", "consulta-sin-top", n, "Sin $top: devuelve hasta el límite por defecto y oculta registros sobre él. Fijar $top (o paginación explícita).")
        if t == "If":
            a_then = json.dumps(a.get("actions", {}), sort_keys=True)
            a_else = json.dumps((a.get("else") or {}).get("actions", {}), sort_keys=True)
            if a_else != "{}" and len(a_then) > 400:
                strip = lambda s: re.sub(r"_(\d+|[A-Z]{1,4})\b|\"[^\"]*@[^\"]*\"", "", s)
                ta, ea = set(re.findall(r'"type": "(\w+)"', a_then)), set(re.findall(r'"type": "(\w+)"', a_else))
                if ta == ea and abs(len(a_then) - len(a_else)) / len(a_then) < 0.15:
                    add("ALTA", "ramas-duplicadas", n, "then/else casi idénticas: solo cambia un dato. Calcular ese dato antes (variable/Compose con if()) y dejar UNA rama.")
        if DEFAULT_NAME.match(n):
            add("BAJA", "nombre-por-defecto", n, "Nombre genérico: renombrar por intención (ej. 'Buscar equipo por nombre') para que el historial de ejecuciones sea legible.")
        s = json.dumps(a.get("inputs", {}), ensure_ascii=False)
        if re.search(r"addHours\(.*?,\s*-?\d+\s*[,)]", s):
            add("MEDIA", "zona-horaria-a-mano", n, "Desfase horario fijo con addHours: se rompe con el horario de verano. Usar convertTimeZone(..., 'UTC', 'Pacific SA Standard Time').")
        for mail in set(EMAIL.findall(s)):
            add("MEDIA", "dato-duro", n, f"Correo fijo `{mail}`: moverlo a variable de entorno o lista de configuración.")
        if t == "InitializeVariable" and depth > 0:
            add("BAJA", "variable-anidada", n, "Initialize variable solo es válido a nivel raíz.")

    # unused variables
    for n, a, *_ in acts:
        if a.get("type") == "InitializeVariable":
            for v in a["inputs"].get("variables", []):
                if raw.count(f"variables('{v['name']}')") == 0:
                    add("BAJA", "variable-sin-uso", n, f"`{v['name']}` nunca se lee.")
    # trigger
    for k, t in d.get("triggers", {}).items():
        if not t.get("conditions") and t.get("type") != "Request":
            add("INFO", "trigger-sin-condicion", k, "Sin condiciones de desencadenador: cada evento consume una ejecución. Si hay eventos que no importan, filtrarlos con trigger conditions.")

    order = {"ALTA": 0, "MEDIA": 1, "BAJA": 2, "INFO": 3}
    groups = {}
    for sev, rule, where, msg in find:
        g = groups.setdefault((sev, rule), {"where": [], "msgs": []})
        g["where"].append(where)
        if msg not in g["msgs"]:
            g["msgs"].append(msg)
    print(f"acciones: {len(acts)}  | hallazgos: {dict(Counter(x[0] for x in find))}")
    for (sev, rule), g in sorted(groups.items(), key=lambda kv: order[kv[0][0]]):
        print(f"\n[{sev}] {rule} ×{len(g['where'])} @ {', '.join(dict.fromkeys(g['where']))}")
        for m in g["msgs"][:3]:
            print(f"   {m}")


# ---------------------------------------------------------------- runs
def cmd_runs(args):
    env, flow, rest = parse_target(args)
    top = rest[rest.index("--top") + 1] if "--top" in rest else "25"
    q = f"{base(env, flow)}/runs?{API_VER}&$top={top}"
    if "--status" in rest:
        q += "&$filter=" + urllib.parse.quote(f"status eq '{rest[rest.index('--status') + 1]}'")
    r = http(q)
    rows = r.get("value", [])
    if not rows:
        trig = next(iter(http(f"{base(env, flow)}?{API_VER}&$expand=properties.definition")["properties"]["definition"]["triggers"]))
        h = http(f"{base(env, flow)}/triggers/{urllib.parse.quote(trig)}/histories?{API_VER}&$top={top}").get("value", [])
        print(f"0 ejecuciones y {len(h)} eventos de trigger en la ventana de retención (~28 días).")
        for x in h:
            p = x["properties"]
            print(f"  trigger {p.get('startTime')}  {p.get('status')}  fired={p.get('fired')}  {(p.get('error') or {}).get('message', '')[:160]}")
    for x in rows:
        p = x["properties"]
        err = (p.get("error") or {}).get("message", "")
        print(f"{x['name']}  {p.get('startTime')}  {p.get('status'):<10} {p.get('trigger', {}).get('name', '')}  {err[:160]}")
    print(f"\nestados: {dict(Counter(x['properties'].get('status') for x in rows))}")


def cmd_run(args):
    env, flow, rest = parse_target(args)
    run = rest[0]
    r = http(f"{base(env, flow)}/runs/{run}/actions?{API_VER}")
    for x in sorted(r.get("value", []), key=lambda x: x["properties"].get("startTime") or ""):
        p = x["properties"]
        line = f"{p.get('status'):<10} {x['name']}  {p.get('code', '')}"
        if p.get("error") and p.get("status") not in ("Skipped", "Succeeded"):
            line += f"\n    error: {json.dumps(p['error'], ensure_ascii=False)[:400]}"
        if p.get("status") == "Failed" and p.get("outputsLink"):
            try:
                body = http(p["outputsLink"]["uri"], auth=False)
                line += f"\n    outputs: {json.dumps(body, ensure_ascii=False)[:600]}"
            except SystemExit as e:
                line += f"\n    outputs: (no disponible: {str(e)[:80]})"
        if p.get("repetitionCount"):
            line += f"  repeticiones: {p['repetitionCount']}"
        print(line)


def cmd_list(args):
    env, needle = args[0], (args[1].lower() if len(args) > 1 else "")
    url = f"https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/{env}/flows?{API_VER}"
    while url:
        r = http(url)
        for x in r.get("value", []):
            p = x["properties"]
            if needle in (p.get("displayName") or "").lower():
                print(f"{x['name']}  {p.get('state'):<9} {p.get('lastModifiedTime', '')[:10]}  {p.get('displayName')}")
        url = r.get("nextLink")


if __name__ == "__main__":
    cmds = {"get": cmd_get, "lint": cmd_lint, "runs": cmd_runs, "run": cmd_run, "list": cmd_list}
    if len(sys.argv) < 3 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    cmds[sys.argv[1]](sys.argv[2:])
