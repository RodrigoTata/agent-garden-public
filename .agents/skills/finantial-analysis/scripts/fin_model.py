#!/usr/bin/env python3
"""Motor de cálculo determinista de finantial-analysis.

Lee un modelo JSON (esquema en ../references/modelo.md), proyecta flujos
mensuales por candidata y escenario, y calcula VAN, TIR, payback, exposición
de caja, valor esperado (Monte Carlo con camino de fallo), tornado y valores
de quiebre.

Uso:
  python fin_model.py modelo.json [--out resultados.json] [--csv flujos.csv]
                                  [--md resumen.md] [--sims 5000] [--seed 42]

Solo librería estándar.
"""
import argparse
import csv
import json
import random
import sys
from itertools import accumulate

DRIVERS = ["volumen", "precio", "costo_variable", "costos_fijos",
           "inversion", "crecimiento", "churn"]

# Asimétricos a propósito: corrigen el sesgo optimista (el pesimista castiga
# más de lo que el optimista premia; la inversión solo puede sobrecostarse).
ESCENARIOS_DEFAULT = {
    "pesimista": {"volumen": 0.6, "precio": 0.9, "costo_variable": 1.1,
                  "costos_fijos": 1.15, "inversion": 1.3,
                  "crecimiento": 0.5, "churn": 1.5},
    "optimista": {"volumen": 1.3, "precio": 1.05, "costo_variable": 0.95,
                  "costos_fijos": 0.95, "inversion": 1.0,
                  "crecimiento": 1.3, "churn": 0.8},
}
BASE = {d: 1.0 for d in DRIVERS}


# ---------------------------------------------------------------- proyección

def rangos(model, cand):
    """driver -> (multiplicador pesimista, multiplicador optimista)."""
    esc = {k: dict(v) for k, v in ESCENARIOS_DEFAULT.items()}
    for nombre, over in model.get("escenarios", {}).items():
        esc.setdefault(nombre, {}).update(over)
    out = {d: (esc["pesimista"][d], esc["optimista"][d]) for d in DRIVERS}
    for d, par in cand.get("rangos", {}).items():
        out[d] = (par[0], par[1])
    return out


def escenario(model, cand, nombre):
    if nombre == "base":
        return dict(BASE)
    idx = 0 if nombre == "pesimista" else 1
    return {d: r[idx] for d, r in rangos(model, cand).items()}


def proyectar(model, cand, mult, hasta=None):
    """Filas mensuales (mes 0..hasta). hasta=None -> horizonte completo."""
    H = model["horizonte_meses"]
    ultimo = H if hasta is None else min(H, hasta)
    tasa_imp = model.get("tasa_impuesto", 0.0)
    costo_hora = model.get("valor_hora_fundador", 0.0) * cand.get("horas_fundador_mes", 0.0)
    activos = {}
    arrastre = 0.0
    filas = []
    for m in range(ultimo + 1):
        ingresos = cvar = 0.0
        for i, ln in enumerate(cand.get("lineas_ingreso", [])):
            inicio = ln.get("mes_inicio", 1)
            if m < inicio:
                continue
            k = m - inicio
            g = ln.get("crecimiento_mensual", 0.0) * mult["crecimiento"]
            tope = ln.get("tope_unidades")
            if ln.get("modo", "transaccional") == "recurrente":
                nuevas = ln["altas_mes"] * mult["volumen"] * (1 + g) ** k
                if tope is not None:
                    nuevas = min(nuevas, tope * mult["volumen"])
                churn = min(1.0, ln.get("churn_mensual", 0.0) * mult["churn"])
                activos[i] = activos.get(i, 0.0) * (1 - churn) + nuevas
                unidades = activos[i]
                cvar += ln.get("cac", 0.0) * mult["costo_variable"] * nuevas
            else:
                unidades = ln["unidades_mes"] * mult["volumen"] * (1 + g) ** k
                if tope is not None:
                    unidades = min(unidades, tope * mult["volumen"])
            ingresos += unidades * ln["precio"] * mult["precio"]
            cvar += unidades * ln.get("costo_variable", 0.0) * mult["costo_variable"]
        fijos = sum(c["monto_mes"] * mult["costos_fijos"]
                    for c in cand.get("costos_fijos", [])
                    if c.get("mes_inicio", 1) <= m <= c.get("mes_fin", H))
        tiempo = costo_hora if m >= 1 else 0.0
        # Impuesto sobre resultado operativo real (el tiempo del fundador es
        # costo de oportunidad imputado, no deducible), con arrastre de pérdidas.
        base_imp = ingresos - cvar - fijos
        if base_imp < 0:
            arrastre -= base_imp
            impuesto = 0.0
        else:
            usado = min(arrastre, base_imp)
            arrastre -= usado
            impuesto = tasa_imp * (base_imp - usado)
        puntuales = sum(p["monto"] * (mult["inversion"] if p.get("tipo") == "capex" else 1.0)
                        for p in cand.get("puntuales", []) if p["mes"] == m)
        if hasta is None and m == H:
            puntuales += cand.get("valor_terminal", 0.0)
        operativo = ingresos - cvar - fijos - tiempo - impuesto
        # flujo = económico (incluye tiempo imputado); caja = lo que sale del bolsillo.
        filas.append({"mes": m, "ingresos": ingresos, "costos_variables": cvar,
                      "costos_fijos": fijos, "tiempo_fundador": tiempo,
                      "impuestos": impuesto, "operativo": operativo,
                      "puntuales": puntuales, "flujo": operativo + puntuales,
                      "caja": operativo + tiempo + puntuales})
    return filas


def exposicion(filas):
    return max(0.0, -min(accumulate(f["caja"] for f in filas)))


def flujos_fallo(model, cand):
    """Camino de fallo: escenario pesimista hasta mes_corte, luego se liquida
    recuperando `recupero_fallo` del capex ya gastado. El capex programado
    después del corte nunca se gasta: ese es el valor de escalonar la apuesta."""
    corte = cand.get("mes_corte", model["horizonte_meses"])
    mult = escenario(model, cand, "pesimista")
    filas = proyectar(model, cand, mult, hasta=corte)
    capex = -sum(p["monto"] * mult["inversion"] for p in cand.get("puntuales", [])
                 if p.get("tipo") == "capex" and p["mes"] <= corte and p["monto"] < 0)
    recupero = cand.get("recupero_fallo", 0.0) * capex
    filas[-1]["puntuales"] += recupero
    filas[-1]["flujo"] += recupero
    filas[-1]["caja"] += recupero
    return filas, corte


# ------------------------------------------------------------------ métricas

def tasa_mensual(model):
    return (1 + model["tasa_descuento_anual"]) ** (1 / 12) - 1


def van(flujos, r):
    return sum(f / (1 + r) ** m for m, f in enumerate(flujos))


def cambios_de_signo(flujos):
    signos = [f > 0 for f in flujos if abs(f) > 1e-9]
    return sum(1 for a, b in zip(signos, signos[1:]) if a != b)


def tir(flujos):
    """TIR mensual por bisección; None si no hay cambio de signo en el VAN."""
    if cambios_de_signo(flujos) == 0:
        return None
    lo, hi = -0.9999, 1.0
    f_lo = van(flujos, lo)
    while van(flujos, hi) * f_lo > 0 and hi < 1e4:
        hi *= 2
    if van(flujos, hi) * f_lo > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = van(flujos, mid)
        if f_mid * f_lo > 0:
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return (lo + hi) / 2


def payback(acumulado):
    """Primer mes desde el cual el acumulado ya no vuelve a ser negativo."""
    if acumulado[-1] < 0:
        return None
    negativos = [m for m, a in enumerate(acumulado) if a < 0]
    return negativos[-1] + 1 if negativos else 0


def metricas(filas, r):
    flujos = [f["flujo"] for f in filas]
    acum = list(accumulate(flujos))
    acum_desc = list(accumulate(f / (1 + r) ** m for m, f in enumerate(flujos)))
    expo = exposicion(filas)
    v = van(flujos, r)
    t = tir(flujos)
    equilibrio = next((f["mes"] for f in filas if f["mes"] >= 1 and f["operativo"] >= 0), None)
    return {
        "van": v,
        "van_sin_tiempo_fundador": van([f["caja"] for f in filas], r),
        "tir_anual": (1 + t) ** 12 - 1 if t is not None else None,
        "tir_ambigua": cambios_de_signo(flujos) > 1,
        "payback_mes": payback(acum),
        "payback_descontado_mes": payback(acum_desc),
        "exposicion_caja": expo,
        "van_por_peso_expuesto": v / expo if expo > 0 else None,
        "mes_equilibrio_operativo": equilibrio,
        "flujo_acumulado_final": acum[-1],
    }


def drivers_aplicables(cand):
    lineas = cand.get("lineas_ingreso", [])
    out = ["volumen", "precio", "costo_variable", "costos_fijos"]
    if any(p.get("tipo") == "capex" for p in cand.get("puntuales", [])):
        out.append("inversion")
    if any(ln.get("crecimiento_mensual", 0) for ln in lineas):
        out.append("crecimiento")
    if any(ln.get("modo") == "recurrente" for ln in lineas):
        out.append("churn")
    return out


def van_con(model, cand, mult, r):
    return van([f["flujo"] for f in proyectar(model, cand, mult)], r)


def tornado(model, cand, r):
    rg = rangos(model, cand)
    barras = []
    for d in drivers_aplicables(cand):
        v_pes = van_con(model, cand, {**BASE, d: rg[d][0]}, r)
        v_opt = van_con(model, cand, {**BASE, d: rg[d][1]}, r)
        barras.append({"driver": d, "van_pesimista": v_pes, "van_optimista": v_opt,
                       "swing": abs(v_opt - v_pes)})
    return sorted(barras, key=lambda b: -b["swing"])


def valor_quiebre(model, cand, d, r):
    """Multiplicador del driver `d` que lleva el VAN base a 0 (None si no cruza)."""
    f = lambda x: van_con(model, cand, {**BASE, d: x}, r)
    f1 = f(1.0)
    for borde in (0.0, 10.0):
        if f(borde) * f1 < 0:
            a, b = (borde, 1.0) if borde < 1 else (1.0, borde)
            fa = f(a)
            for _ in range(80):
                mid = (a + b) / 2
                fm = f(mid)
                if fm * fa > 0:
                    a, fa = mid, fm
                else:
                    b = mid
            return (a + b) / 2
    return None


def percentil(ordenados, p):
    return ordenados[int(round(p * (len(ordenados) - 1)))]


def monte_carlo(model, cands, r, fallos, sims, seed):
    """fallos[i] = (van, exposición de caja) del camino de fallo de la candidata i."""
    rnd = random.Random(seed)
    rgs = [rangos(model, c) for c in cands]
    aplic = [drivers_aplicables(c) for c in cands]
    vans = [[] for _ in cands]
    expos = [[] for _ in cands]
    ganadas = [0] * (len(cands) + 1)  # último índice = opción cero
    for _ in range(sims):
        ronda = []
        for i, c in enumerate(cands):
            if rnd.random() > c.get("p_exito", 1.0):
                v, e = fallos[i]
            else:
                mult = dict(BASE)
                for d in aplic[i]:
                    pes, opt = rgs[i][d]
                    mult[d] = rnd.triangular(min(pes, opt, 1.0), max(pes, opt, 1.0), 1.0)
                filas = proyectar(model, c, mult)
                v, e = van([f["flujo"] for f in filas], r), exposicion(filas)
            vans[i].append(v)
            expos[i].append(e)
            ronda.append(v)
        ronda.append(0.0)
        ganadas[max(range(len(ronda)), key=lambda j: ronda[j])] += 1
    out = []
    for i in range(len(cands)):
        s = sorted(vans[i])
        out.append({"p10": percentil(s, 0.10), "p50": percentil(s, 0.50),
                    "p90": percentil(s, 0.90), "media": sum(s) / len(s),
                    "p_van_negativo": sum(1 for v in s if v < 0) / len(s),
                    "p_mejor": ganadas[i] / sims,
                    "exposicion_caja_p90": percentil(sorted(expos[i]), 0.90)})
    return out, ganadas[-1] / sims


# ---------------------------------------------------------------- validación

def validar(model):
    errores = []
    for k in ("horizonte_meses", "tasa_descuento_anual", "candidatas"):
        if k not in model:
            errores.append(f"falta el campo obligatorio '{k}'")
    criterio = model.get("criterio_ranking", "valor_esperado")
    if criterio not in ("valor_esperado", "valor_esperado_por_peso", "p_mejor"):
        errores.append(f"criterio_ranking desconocido '{criterio}'")
    ids = set()
    for c in model.get("candidatas", []):
        cid = c.get("id", "?")
        if cid in ids:
            errores.append(f"id duplicado '{cid}'")
        ids.add(cid)
        for ln in c.get("lineas_ingreso", []):
            campo = "altas_mes" if ln.get("modo") == "recurrente" else "unidades_mes"
            for req in (campo, "precio"):
                if req not in ln:
                    errores.append(f"{cid}/{ln.get('concepto', '?')}: falta '{req}'")
    return errores


def alertas_de(model, cand):
    a = []
    if "p_exito" not in cand:
        a.append("p_exito no declarado: se asumió 1.0 (el camino de fallo no pesa)")
    if "mes_corte" not in cand:
        a.append("mes_corte no declarado: el camino de fallo corre todo el horizonte")
    for ln in cand.get("lineas_ingreso", []):
        if ln.get("costo_variable", 0) >= ln["precio"]:
            a.append(f"'{ln.get('concepto', '?')}': margen de contribución <= 0")
    if not cand.get("horas_fundador_mes"):
        a.append("horas_fundador_mes no declarado: el tiempo del fundador queda sin costear")
    return a


# ------------------------------------------------------------------- informe

def fmt(x):
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def pct(x):
    return "—" if x is None else f"{x * 100:.1f}%"


def ratio(x):
    return "—" if x is None else f"{x:.2f}"


def mes(x):
    return "no recupera" if x is None else f"mes {x}"


def resumen_md(model, res):
    p = res["parametros"]
    L = [f"# Resultados del modelo — {model.get('titulo', 'sin título')}", "",
         f"Moneda: {p['moneda']} · Horizonte: {p['horizonte_meses']} meses · "
         f"Tasa de descuento: {pct(p['tasa_descuento_anual'])} anual · "
         f"Impuesto: {pct(p['tasa_impuesto'])} · Simulaciones: {p['simulaciones']}", "",
         f"## Ranking (criterio: {p['criterio_ranking']})", "",
         "| # | Candidata | Valor esperado | VAN base | VAN pesim. | VAN optim. | TIR base | "
         "Payback desc. | Exposición caja P90 | V. esperado / peso | P(VAN<0) | P(mejor) | Filtros |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, cid in enumerate(res["ranking"], 1):
        c = res["candidatas"][cid]
        b, pe, op = (c["escenarios"][k] for k in ("base", "pesimista", "optimista"))
        mc = c["montecarlo"]
        filtros = "OK" if c["filtros"]["ok"] else "NO: " + "; ".join(c["filtros"]["motivos"])
        L.append(f"| {n} | {c['nombre']} | {fmt(c['montecarlo']['media'])} | {fmt(b['van'])} | "
                 f"{fmt(pe['van'])} | {fmt(op['van'])} | {pct(b['tir_anual'])} | "
                 f"{mes(b['payback_descontado_mes'])} | {fmt(mc['exposicion_caja_p90'])} | "
                 f"{ratio(c['valor_esperado_por_peso'])} | "
                 f"{pct(mc['p_van_negativo'])} | {pct(mc['p_mejor'])} | {filtros} |")
    L.append(f"| — | Opción cero (no invertir) | 0 | 0 | 0 | 0 | — | — | 0 | — | 0.0% | "
             f"{pct(res['opcion_cero_p_mejor'])} | OK |")
    L += ["", "## Supuesto crítico y valor de quiebre", "",
          "| Candidata | Supuesto crítico | Swing de VAN | Valor de quiebre (VAN = 0) | Pérdida de caja si falla |",
          "|---|---|---|---|---|"]
    for cid in res["ranking"]:
        c = res["candidatas"][cid]
        sc = c["supuesto_critico"]
        q = sc["quiebre_multiplicador"] if sc else None
        quiebre = "no cruza en [0, 10]" if q is None else f"×{q:.2f} ({(q - 1) * 100:+.0f}% vs base)"
        L.append(f"| {c['nombre']} | {sc['driver'] if sc else '—'} | {fmt(sc['swing'] if sc else None)} | "
                 f"{quiebre} | {fmt(c['fallo']['perdida_caja'])} (corte mes {c['fallo']['mes_corte']}) |")
    if model.get("valor_hora_fundador"):
        L += ["", "## Dependencia del tiempo del fundador", "",
              "| Candidata | VAN base | VAN base sin costear horas | Horas/mes |", "|---|---|---|---|"]
        for cid, c in zip(res["ranking"], (res["candidatas"][k] for k in res["ranking"])):
            b = c["escenarios"]["base"]
            horas = next(x.get("horas_fundador_mes", 0) for x in model["candidatas"] if x["id"] == cid)
            L.append(f"| {c['nombre']} | {fmt(b['van'])} | {fmt(b['van_sin_tiempo_fundador'])} | {horas} |")
    for cid in res["ranking"]:
        c = res["candidatas"][cid]
        L += ["", f"### Tornado — {c['nombre']}", "",
              "| Driver | VAN pesim. | VAN optim. | Swing | Quiebre |", "|---|---|---|---|---|"]
        for t in c["tornado"]:
            q = c["quiebres"].get(t["driver"])
            L.append(f"| {t['driver']} | {fmt(t['van_pesimista'])} | {fmt(t['van_optimista'])} | "
                     f"{fmt(t['swing'])} | {'—' if q is None else f'×{q:.2f}'} |")
    alertas = [(res["candidatas"][cid]["nombre"], a)
               for cid in res["ranking"] for a in res["candidatas"][cid]["alertas"]]
    if alertas:
        L += ["", "## Alertas", ""] + [f"- **{n}**: {a}" for n, a in alertas]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------------- main

def correr(model, sims, seed):
    r = tasa_mensual(model)
    cands = model["candidatas"]
    res = {"parametros": {
        "moneda": model.get("moneda", "CLP"),
        "horizonte_meses": model["horizonte_meses"],
        "tasa_descuento_anual": model["tasa_descuento_anual"],
        "tasa_impuesto": model.get("tasa_impuesto", 0.0),
        "criterio_ranking": model.get("criterio_ranking", "valor_esperado"),
        "simulaciones": sims, "semilla": seed}, "candidatas": {}}
    fallos = []
    for c in cands:
        esc = {n: metricas(proyectar(model, c, escenario(model, c, n)), r)
               for n in ("base", "pesimista", "optimista")}
        ff, corte = flujos_fallo(model, c)
        vf = van([f["flujo"] for f in ff], r)
        fallos.append((vf, exposicion(ff)))
        torn = tornado(model, c, r)
        quiebres = {t["driver"]: valor_quiebre(model, c, t["driver"], r) for t in torn}
        critico = None
        if torn and torn[0]["swing"] > 0:
            critico = {"driver": torn[0]["driver"], "swing": torn[0]["swing"],
                       "quiebre_multiplicador": quiebres[torn[0]["driver"]]}
        res["candidatas"][c["id"]] = {
            "nombre": c.get("nombre", c["id"]), "escenarios": esc,
            "fallo": {"van": vf, "perdida_caja": max(0.0, -sum(f["caja"] for f in ff)),
                      "mes_corte": corte},
            "p_exito": c.get("p_exito", 1.0),
            "tornado": torn, "quiebres": quiebres, "supuesto_critico": critico,
            "alertas": alertas_de(model, c)}
    mc, p_cero = monte_carlo(model, cands, r, fallos, sims, seed)
    res["opcion_cero_p_mejor"] = p_cero
    for c, m in zip(cands, mc):
        rc = res["candidatas"][c["id"]]
        rc["montecarlo"] = m
        expo = m["exposicion_caja_p90"]
        rc["valor_esperado"] = m["media"]
        rc["valor_esperado_por_peso"] = m["media"] / expo if expo > 0 else None
        motivos = []
        cap = model.get("capital_disponible")
        if cap is not None and expo > cap:
            motivos.append(f"exposición de caja P90 {fmt(expo)} > capital {fmt(cap)}")
        tol = model.get("perdida_maxima_tolerable")
        if tol is not None and rc["fallo"]["perdida_caja"] > tol:
            motivos.append(f"pérdida si falla {fmt(rc['fallo']['perdida_caja'])} > tolerable {fmt(tol)}")
        horas = model.get("horas_disponibles_mes")
        if horas is not None and c.get("horas_fundador_mes", 0) > horas:
            motivos.append(f"{c['horas_fundador_mes']} h/mes > {horas} h disponibles")
        rc["filtros"] = {"ok": not motivos, "motivos": motivos}
    clave = {
        "valor_esperado": lambda k: res["candidatas"][k]["valor_esperado"],
        "valor_esperado_por_peso": lambda k: res["candidatas"][k]["valor_esperado_por_peso"] or float("-inf"),
        "p_mejor": lambda k: res["candidatas"][k]["montecarlo"]["p_mejor"],
    }[res["parametros"]["criterio_ranking"]]
    res["ranking"] = sorted(res["candidatas"],
                            key=lambda k: (not res["candidatas"][k]["filtros"]["ok"], -clave(k)))
    return res


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("modelo")
    ap.add_argument("--out", help="resultados JSON")
    ap.add_argument("--csv", help="flujos mensuales del escenario base")
    ap.add_argument("--md", help="resumen Markdown (por defecto solo a stdout)")
    ap.add_argument("--sims", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    with open(args.modelo, encoding="utf-8") as fh:
        model = json.load(fh)
    errores = validar(model)
    if errores:
        sys.exit("Modelo inválido:\n- " + "\n- ".join(errores))

    res = correr(model, args.sims, args.seed)
    md = resumen_md(model, res)
    print(md)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(md)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
    if args.csv:
        campos = ["candidata", "mes", "ingresos", "costos_variables", "costos_fijos",
                  "tiempo_fundador", "impuestos", "operativo", "puntuales", "flujo", "caja",
                  "acumulado"]
        with open(args.csv, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=campos)
            w.writeheader()
            for c in model["candidatas"]:
                acum = 0.0
                for f in proyectar(model, c, BASE):
                    acum += f["flujo"]
                    w.writerow({"candidata": c["id"], **{k: round(v, 2) for k, v in f.items()},
                                "acumulado": round(acum, 2)})


if __name__ == "__main__":
    main()
