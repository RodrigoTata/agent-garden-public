---
name: agile-prototype
description: Plan and execute an agile prototyping effort — software or physical product — through iterative Marks (MKI, MKII, MKIII…). Use when the user wants to prototype a new product, plan hardware iterations, build an MVP with a clear upgrade path, or mentions "agile prototype", "MKI", "mark", or "prototype iteration".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

An idea has arrived — a product to build, physical or digital. This skill charts the path from foggy concept to validated prototype through **Marks**: numbered iterations (MKI, MKII…) that each answer one question and close decisions before investing in the next.

The leading word is **Mark** — a self-contained iteration of the whole product at a specific fidelity, built to answer one central question.

## 1. Ground the vision

Run a `/grill-with-docs` session to pin down four things — stop when all four are sharp:

1. **Vision**: What the world looks like when this product exists and works.
2. **Mission**: The concrete problem this prototype solves, for whom, and the constraint envelope (budget, timeline, tools available).
3. **Domain**: Whether the effort is *manufacturing* (physical product, BOM, 3D printing, electronics), *software* (code, APIs, UI), or *hybrid* (firmware + hardware + cloud, like IoT).
4. **Success signal**: How the user will know the first Mark worked — a testable, observable outcome, not a feeling.

Capture the four answers as a `vision.md` in the project's `docs/` directory. This is the project's north star — every Mark orients to it.

## 2. Chart the Marks

Run `/wayfinder` to create a map whose **destination** is the vision from Step 1. The wayfinder map becomes the project's decision tracker.

While charting, identify and sequence the Marks. Each Mark is a self-contained prototype answering **one central question**:

| Mark | Question pattern | Fidelity |
| :--- | :--- | :--- |
| **MKI** | "Does the core idea work at all?" | Low — off-the-shelf parts, generic stack, cheap materials |
| **MKI-b** | "Is there a cheaper/simpler alternative?" | Low — same function, different trade-offs |
| **MKII** | "Does it work under real conditions?" | Medium — custom parts, real integrations, user testing |
| **MKIII** | "Can it be produced/deployed at scale?" | High — DFM, CI/CD, monitoring, production materials |

Create a `version_log.md` in the project's `docs/` directory. For each Mark, document:

```markdown
## Version: MK[N] — [Descriptive Name]
*Central Question:* [What this Mark validates]
*Target Date:* [When]
*Estimated Cost:* [Budget]

### Decisions
- [Decision 1]: [Choice] — [Rationale]

### BOM / Tech Stack
| Component | Description | Cost |
| :--- | :--- | :--- |

### Lessons Learned
- [What was learned that informs MK[N+1]]
```

**Completion criterion**: Every planned Mark has a central question, and the first Mark (MKI) has a complete BOM/Stack and cost estimate.

## 3. Spec the first Mark

For the MKI specifically, produce these artifacts:

- **Shopping List / BOM** (manufacturing) or **Tech Stack doc** (software): Use `/research` and `/quotation-for` to price every component. Save as `docs/[project]-MKI-shoppinglist.md` or `.html`.
- **Architecture doc**: How the pieces connect — layers, protocols, interfaces. Save as `docs/architecture.md`.
- **Wayfinder tickets**: One decision ticket per open question in MKI, using the wayfinder map from Step 2. Resolve them via `/grill-with-docs` or `/research` before building.
- **Out of Scope**: Explicitly list what MKI will NOT solve. Write it in the wayfinder map's Out of Scope section and in `version_log.md`.

**Completion criterion**: MKI has a priced BOM/Stack, an architecture doc, no unresolved decision tickets, and a declared Out of Scope.

## 4. Build the Mark

Execute the MKI — write code, order parts, print 3D pieces, wire circuits. This is the only step that produces the physical or digital prototype.

Track progress using the wayfinder map's tickets. As decisions are made during construction, close tickets and update `version_log.md` with lessons learned.

**Sub-versions**: If during build you discover a legitimate trade-off alternative (e.g., cheaper brain, different framework), create a sub-version (MKI-b) in `version_log.md` with its own BOM/Stack and cost delta.

## 5. Close the Mark

When the central question is answered:

1. Update `version_log.md` with final costs, decisions, and lessons learned.
2. Close all wayfinder tickets for this Mark.
3. Graduate fog from the wayfinder map — decisions that are now specifiable become tickets for MKII.
4. Update the wayfinder map's "Decisions so far" with the Mark's resolved tickets.

**Completion criterion**: The central question has a documented yes/no/qualified answer, lessons are recorded, and MKII's central question is stated.

## 6. Repeat

Return to Step 3 for the next Mark. Each Mark inherits the decisions and lessons of all previous Marks. The cycle ends when the vision from Step 1 is met or the user decides to stop.

---

## Domain-specific guidance

Consult [`references/research-agile-prototyping.md`](references/research-agile-prototyping.md) for the full research document with methodology details and source citations.

### Manufacturing projects
- BOM is the primary artifact — every component priced with supplier and lead time.
- Use `/quotation-for` to find local pricing (defaults to Chile, or user location).
- Track 3D printing costs separately (material weight × $/kg + energy).
- Sub-versions (MKI-a, MKI-b) are common when evaluating commercial vs. DIY alternatives.
- MKI uses off-the-shelf, no-solder, plug-and-play components.

### Software projects
- Tech Stack doc replaces BOM — frameworks, services, hosting, estimated monthly cost.
- MKI is a functional MVP, not a mockup — it must run and be testable by a user.
- Architecture doc covers API boundaries, data flow, and auth strategy.
- Use `/tdd` during Build (Step 4) for test-driven development.
- Sub-versions compare framework choices (e.g., MKI-a with Firebase vs. MKI-b with Supabase).

### Hybrid (IoT / firmware + cloud)
- Two parallel tracks: hardware BOM + software stack, documented separately.
- Architecture doc must show the boundary between Edge (local) and Cloud (remote).
- Failsafe mechanisms (timeouts, offline mode) are MKI requirements, not MKII.
- Telemetry protocol (MQTT, HTTP) is a wayfinder decision ticket in Step 3.
