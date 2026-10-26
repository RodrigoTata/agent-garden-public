# Research: Agile Prototyping — MKI / MKII / MKIII Methodology

> Primary research on the *Agile Prototyping* methodology applied to both software development and physical product manufacturing.

---

## 1. What is Agile Prototyping?

**Agile Prototyping** is an iterative product development methodology that replaces the linear "Waterfall" approach (design everything → build everything → test everything) with short **build-test-learn** cycles called **Marks** (MKI, MKII, MKIII...).

Each *Mark* is a complete iteration of the product — not an incremental patch, but a **version of the entire system** with an increasing level of fidelity. The core idea is that each Mark answers a specific question and closes design decisions before investing resources in the next iteration.

### Guiding Principle

> *"Fail early, fail cheap, converge fast."*

The goal is not the perfect product on the first try. The goal is to **eliminate uncertainty** as quickly and cheaply as possible by iterating on functional prototypes that can be touched, tested, and critiqued.

### Key differences with other methodologies

| Concept | Agile Prototyping | Lean Prototyping | Waterfall |
| :--- | :--- | :--- | :--- |
| **Focus** | Functional iterations of the whole product (MKI → MKII) | Eliminate waste, validate minimum hypotheses | Complete design before building |
| **Deliverable** | One functional prototype per iteration | A minimum MVP to validate the market | The final product |
| **Cost of error** | Low (detected in MKI/MKII) | Low (fast pivots) | High (detected at the end) |
| **Naming** | Mark I, Mark II, Mark III... | MVP, Pivot | v1.0, v2.0 |
| **Natural domain** | Hardware + Software + Manufacturing | Startups, business validation | Civil/aerospace engineering |

---

## 2. The Mark System (MKI, MKII, MKIII...)

### Origin of the term

"Mark" (abbreviated **MK** or **Mk**) comes from the identification plates used in military equipment and industrial machinery to designate successive modifications to the same base design. Today it is universally used in product engineering, electronics, automotive, and manufacturing.

### Structure of each Mark

Each Mark has 4 mandatory components:

```
MK[N] — [Descriptive Name]
├── Central Question:  What is this iteration trying to validate?
├── BOM / Stack:       Bill of Materials (hardware) or tech stack (software)
├── Decisions:         What was decided and why (ADRs / Closed Tickets)
└── Lessons Learned:   What was learned to inform MK[N+1]
```

### Typical progression

| Mark | Focus | Fidelity | Typical question |
| :--- | :--- | :--- | :--- |
| **MKI** | Proof of Concept | Low — Generic/off-the-shelf components, cheap materials | "Does the core idea work?" |
| **MKI-b** | Cheap/alternative variant of MKI | Low — Same function, different approach | "Is there a cheaper/simpler way?" |
| **MKII** | Engineering Prototype | Medium — Closer to final components, custom PCBs, 3D parts | "Does it work as intended in real conditions?" |
| **MKIII** | Pre-production | High — Final materials, DFM (Design for Manufacturing) | "Can it be mass-produced?" |
| **MK-Production** | Final product | Production — Tooling, molds, QA | "Is it ready for the end user?" |

### Sub-versions (MKI-a, MKI-b)

When an iteration generates variants (for example, an expensive vs. a cheap option), sub-versions with an alphabetical suffix are used:

- **MKI-a**: Original version (e.g., M5Stack Tough with touch screen)
- **MKI-b**: Alternative variant (e.g., ESP32 Headless in IP65 box without screen)

Both validate the same question but with different trade-offs (cost vs. capability).

---

## 3. Pattern of Marks

Each Mark answers one question and closes with a decision:

```
MKI  → "Does it work?"         → Generic components, cheap parts, consumable sensors
MKIb → "Is it cheaper?"        → Alternative variant with a lower-cost brain or enclosure
3D   → "Is it manufacturable?" → Custom printed parts replacing commercial ones
MKII → "Does it scale?"        → Migration to a professional architecture
```

---

## 4. Application in Software

The same methodology applies to software development, replacing the BOM with a Tech Stack:

| Mark | Software equivalent | Example |
| :--- | :--- | :--- |
| **MKI** | Functional MVP with minimum stack | Landing page + form + Firebase |
| **MKI-b** | Variant with a different framework/stack | Same MVP but in Next.js instead of static HTML |
| **MKII** | Real integration, APIs, auth, DB | NestJS Backend + PostgreSQL + Real Auth |
| **MKIII** | Optimization, tests, CI/CD, monitoring | Full pipeline, E2E testing, logging |
| **Production** | Production deploy with SLA | Cloud Run + monitoring + alerts |

### Concrete Example (Software)

```
MKI   → "Does the user understand the flow?"   → Clickable HTML mockup
MKI-b → "Does it work with real data?"         → Connected to a mock API
MKII  → "Does it scale with multiple users?"   → Real backend, auth, DB
MKIII → "Is it maintainable and testable?"     → Tests, CI/CD, docs
```

---

## 5. Artifacts for each Mark

Each iteration generates and consumes specific artifacts:

### Input artifacts (created BEFORE building)

| Artifact | Description | Associated skill |
| :--- | :--- | :--- |
| **Vision & Mission** | What problem the project solves and for whom | `/grill-with-docs` |
| **Wayfinder Map** | Map of pending decisions with tickets | `/wayfinder` |
| **Shopping List / BOM** | Materials list with costs and suppliers | `/quotation-for` |
| **Architecture Doc** | Layer diagram and technical decisions | `/grill-with-docs` |
| **Research Docs** | Technical research to inform decisions | `/research` |

### Output artifacts (generated DURING or AFTER building)

| Artifact | Description |
| :--- | :--- |
| **Version Log** | Technical changelog per Mark (what changed, what was learned) |
| **ADRs (Architecture Decision Records)** | Design decisions with context and rationale |
| **Closed Tickets** | Specific decisions documented as resolved issues |
| **Functional Prototype** | The tangible deliverable of the iteration |

---

## 6. Fundamental Principles

1. **One question per Mark.** Each iteration exists to answer ONE central question. If you need to answer two, those are two Marks.

2. **Fidelity proportional to risk.** Don't use expensive materials or production code to validate an early hypothesis. MKI is deliberately cheap.

3. **Document decisions, not just results.** The value of each Mark is not just the prototype, but the decisions it closes. Use Wayfinder tickets or ADRs.

4. **Sub-versions for trade-offs.** When a decision has legitimate alternatives (expensive vs. cheap, screen vs. headless), explore them as MK[N]-a, MK[N]-b.

5. **Explicit Out of Scope.** Each Mark declares what it will NOT solve. This prevents over-engineering and maintains focus.

6. **The Mark closes with a decision, not a perfect product.** The iteration ends when the question is answered, not when the prototype is "pretty".

---

## Sources

- Wikipedia: *Mark (designation)* — Historical origin of the Mark I/II/III naming system in military and industrial equipment.
- IDEO Design Thinking — Principles of rapid prototyping and "fail early, fail often".
- Stanford d.school — Iterative, question-driven prototyping methodology.
- Agile Hardware Development (Trimech, Pacific Research) — Adaptation of Agile to hardware manufacturing.
