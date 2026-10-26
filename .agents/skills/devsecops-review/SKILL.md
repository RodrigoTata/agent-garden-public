---
name: devsecops-review
description: Unified architecture and security review of a codebase.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# DevSecOps Review

Surface architectural friction **and** security exposure in a single pass, then present both as **deepening opportunities** en un reporte visual HTML y también como un **artefacto Markdown persistente**. Every finding is framed in terms of **depth**, **seams**, **locality**, and **leverage** — security flaws are shallow modules by another name.

This skill is _informed_ by the project's domain model and built on a shared design vocabulary:

- Run the `/codebase-design` skill for the architecture vocabulary (**module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, **locality**) and its principles (the deletion test, "the interface is the test surface", "one adapter = hypothetical seam, two = real"). Use these terms exactly — don't drift into "component," "service," "API," or "boundary."
- The domain language in `CONTEXT.md` gives names to good seams; ADRs in `docs/adr/` record decisions this skill should not re-litigate.

> [!IMPORTANT]
> **Analyze and report only.** Do not modify code unless requested.

---

## Process

### 1. Explore

Read the project's domain glossary (`CONTEXT.md`) and any ADRs first. Then walk the codebase organically, looking through two lenses simultaneously:

**Architecture lens** — note where you experience friction:
- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal.

**Security lens** — scan for exposure using the checklist in [SECURITY-CHECKS.md](SECURITY-CHECKS.md). Start with changed files (`git diff --name-only`), then widen to adjacent modules. Classify each finding by severity: `🔴 CRITICAL` (exploitable), `🟡 WARNING` (potential weakness), `🔵 INFO` (defense-in-depth).

Translate every security finding into architectural language: scattered authorization across N controllers is a shallow guard module begging to be deepened; unvalidated DTOs are a missing interface contract. This translation is the core of the merge — security exposure _is_ architectural shallowness.

**Completion criterion**: A bulleted list of candidate findings (architecture and security), each with the affected files and a one-sentence problem statement using `/codebase-design` vocabulary.

---

### 2. Present candidates as HTML and Markdown reports

Debe presentarse el resultado de la auditoría en dos formatos simultáneamente:

**A. Markdown Artifact:**
Crea un artifact en formato Markdown (ej. `devsecops-review.md`). Por cada candidato encontrado, detalla:
- **Files** — which files/modules are involved
- **Problem** — why the current structure causes friction or exposure
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality, leverage, and how tests or security posture improve
- **Recommendation strength** — `Strong`, `Worth exploring`, or `Speculative`
- **Severity** (security cards only) — `🔴`, `🟡`, or `🔵`

**B. Interactive HTML Report:**
Write a self-contained HTML file to the OS temp directory (`%TEMP%` on Windows, `$TMPDIR` or `/tmp` otherwise) as `devsecops-review-<timestamp>.html`. Open it for the user and tell them the absolute path. See [HTML-REPORT.md](HTML-REPORT.md) for the HTML scaffold and styling guidance. Render the same candidate data visually, añadiendo **Diagramas Antes/Después**.

Finaliza ambos reportes con la sección **Top recommendation**: cuál candidato atacar primero y por qué.

**ADR conflicts**: if a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting. Mark it clearly with a warning callout.

> [!CAUTION]
> If `🔴 CRITICAL` security findings exist, flag them prominently and recommend fixing before any architectural work.

Do NOT propose interfaces yet. After the files are written, ask the user: "Which of these would you like to explore?"

**Completion criterion**: Un artefacto Markdown (`devsecops-review.md`) ha sido generado, y además un archivo HTML ha sido creado en el directorio temporal y abierto en el navegador. Ambos contienen los candidatos del Paso 1.

---

### 3. Grilling loop

Once the user picks a candidate, run the `/grilling` skill to walk the design tree — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:
- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term. Create the file lazily if needed.
- **Sharpening a fuzzy term?** Update `CONTEXT.md` right there.
- **User rejects a candidate with a load-bearing reason?** Offer an ADR only when the reason would prevent a future explorer from re-suggesting it.
- **Want to explore alternative interfaces?** Run the `/codebase-design` skill and its design-it-twice pattern.

**Completion criterion**: The selected candidate has a concrete interface proposal reviewed by the user, with `CONTEXT.md` and ADRs updated for any decisions made.

---

## Guardrails

- **Zero Trust**: Assume all client-side validation can be bypassed. If the backend doesn't check the role, it's a vulnerability.
- **Traceability**: Every finding points to a specific file and line.
- **Agent Checks Are Static**: Focus strictly on codebase analysis and static vulnerability detection.
- **Domain fidelity**: Use `CONTEXT.md` vocabulary for the domain, `/codebase-design` vocabulary for the architecture. Never substitute.
