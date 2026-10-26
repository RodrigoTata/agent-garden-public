---
name: start-a-proyect
description: Orchestrate end-to-end inception and execution of physical, hardware/IoT, and digital projects through an integrated pipeline of grilling, 3D modeling, market quotations, and interactive assembly manuals. Use when starting a project, building physical structures, 3D printing gadgets, IoT prototypes, carpentry, or mentions "start a project", "start-a-proyect", "iniciar proyecto", or "nuevo proyecto".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Start a Project (Physical, IoT & Digital Orchestrator)

An idea has arrived — a physical build (carpentry, shade structure, greenhouse), a 3D-printed IoT gadget (sensors, enclosures, microcontrollers), or a software/hybrid product. This skill is the **Master Orchestrator**: it sequences and coordinates specialized skills into an integrated engineering pipeline, delivering a tangible, priced, modeled, and documented project.

The leading words are:
- **Triad**: The three core physical deliverables — (1) Spatial Interactive 3D Twin, (2) Local Sourcing & BOM Quotation, and (3) Living Assembly Manual.
- **Grounding**: Anchoring every design in real-world environmental envelopes (wind, sun, physical walls, local supplier catalogs, and gravitational stability).
- **Mark**: Iterative prototyping stages (MKI proof-of-concept, MKII field validation, MKIII production) via `/agile-prototype`.
- **Dual-Theme**: All visual deliverables default to **dark glassmorphic UI** on screen with a light mode toggle, and strict `@media print` white isolation for paper.

---

## The Orchestration Pipeline

```
  [Idea / Concept]
         │
         ▼
 1. Inception & Scaffolding  ──▶  /repo-format (dirs: prototypes/, docs/, cad/, src/)
         │
         ▼
 2. Grounding & Spec         ──▶  /grill-with-docs + /research + /to-spec
         │                        (produces: docs/GLOSARIO_DOMINIO.md, docs/ADR-*.md)
         ▼
 3. Spatial Digital Twin     ──▶  /interactive-3d-structure
         │                        (produces: prototypes/[project]_3d.html)
         ▼
 4. Sourcing & Quotations    ──▶  /quotation-for (+ /business-implementation-plan if commercial)
         │                        (produces: prototypes/[project]_cotizacion.html)
         ▼
 5. Living Assembly Manual   ──▶  /generate-html-doc + /agile-prototype
         │                        (produces: prototypes/[project]_manual.html, version_log.md)
         ▼
 6. Cross-Linking & Handoff  ──▶  Bi-directional navigation bars linking the Triad
```

---

## Phase 1 — Project Inception & Scaffolding

### Step 1.1: Archetype Classification
Classify the project into one of four archetypes to configure the downstream workflow:

| Archetype | Primary Focus | Mandatory Skills in Pipeline |
| :--- | :--- | :--- |
| **Physical / Structural** | Carpentry, shade structures, greenhouses, furniture, framing | `/grill-with-docs`, `/interactive-3d-structure`, `/quotation-for`, `/generate-html-doc` |
| **Hardware / IoT & 3D Print**| Microcontrollers (ESP32/RP2040), sensors, 3D printed housings, actuators | `/grill-with-docs`, `/research`, `/interactive-3d-structure`, `/quotation-for`, `/generate-html-doc` |
| **Hybrid (Hardware + App)**| Physical devices paired with cloud dashboards, firmware, telemetry | Full pipeline + `/to-spec`, `/agile-prototype`, `/tdd` |
| **Digital / Software** | Pure codebases, web applications, APIs, automation scripts | `/grill-with-docs`, `/to-spec`, `/agile-prototype`, `/repo-format`, `/tdd` |

### Step 1.2: Repository Scaffolding (`/repo-format`)
Run or verify project repository structure:
- `prototypes/` — Interactive HTML deliverables (3D models, dashboards, manuals).
- `docs/` — Architectural Decision Records (`ADR-*.md`), glossary, specs, version logs.
- `cad/` or `3d/` — STL files, OpenSCAD, FreeCAD or parametric source definitions.
- `firmware/` or `src/` — Code, schematics, pinouts, or software logic.

*Completion criterion*: Archetype identified, and target directories (`prototypes/`, `docs/`) confirmed or created.

---

## Phase 2 — Grounding & Engineering Spec

### Step 2.1: Relentless Grilling (`/grill-with-docs`)
Interview the user to stress-test physical, technical, and operational constraints:
- **Zero Modal Dialogs**: Never use the `ask_question` tool. Present questions directly in plain chat text so the user can freely attach docs, images, or slash commands.
- **Cadence**: Ask questions one at a time. For each question, propose two distinct alternatives with your recommendation and technical rationale.
- **Physical Envelopes to Pin Down**:
  - *Boundaries*: Solid walls, parapets, roof membranes, clearances, neighbor boundaries.
  - *Environmental Loads*: Dominant wind directions (e.g. SW gusts), solar trajectory (North in southern hemisphere, South in northern hemisphere), rain drainage, salinity/corrosion.
  - *Fixing vs. Ballast*: Can the substrate be drilled? (e.g., roof waterproofing cannot be pierced $\rightarrow$ gravitational ballast required).
  - *Power & Connectivity*: Battery/solar vs. mains, WiFi/Zigbee range, sleep cycles.

### Step 2.2: Researching Unknowns (`/research`)
If material specifications, structural loads, or electronic components carry ambiguity, invoke `/research`:
- Thermal expansion, outdoor UV degradation (e.g. ASA/PETG vs. PLA for 3D printing; 60 Mesh HDPE vs. Raschel).
- Sizing lumber escuadrías against wind shear and deflection.
- Power budget calculations for battery/solar IoT nodes.

### Step 2.3: Architecture Records & Glossary
Produce the domain foundation:
1. `docs/GLOSARIO_DOMINIO.md`: Canonical terms, materials, and units.
2. `docs/ADR-[0001..N]-[decision].md`: Document each architectural decision (why ballast was chosen over anchors, why 60 Mesh was selected, etc.).
3. `docs/spec.md`: Formal functional requirements synthesized via `/to-spec`.

*Completion criterion*: At least 2 resolved ADRs, a domain glossary, and an unambiguous physical/technical specification.

---

## Phase 3 — Spatial & Structural Digital Twin (`/interactive-3d-structure`)

*(Mandatory for Physical and Hardware/IoT archetypes)*

Create an interactive 3D digital twin in `prototypes/[project]_3d.html`:

1. **Parametric Seam (`STRUCTURE_SPEC`)**:
   - Declare every piece, lumber beam, profile, 3D printed shell, or PCB in a top-level JavaScript configuration object.
2. **Cardinal & Spatial Anchors**:
   - **Compass Gizmo**: Corner orientation cube showing North, South, East, West, Zenith.
   - **Ground Grid & Compass Rose**: Cardinal alignment aligned to solar and wind fronts.
   - **3D Measurement Lines (Cotas)**: Interactive dimensions ($X, Y, Z$) directly in 3D space.
   - **Scale Reference**: Human figure (1.75m) or familiar hand-held object.
3. **Layer Filtering & Render Modes**:
   - Checkbox toggles for each subsystem: Framing/Chassis, Enclosures/Meshes, Hardware, Plantings/Sensors, Dimensions.
   - Render switches: Solid Natural, X-Ray Transparent, and Wireframe.
4. **Interactive Inspection**:
   - Hover tooltips showing commercial piece names, cut dimensions, and material types.
5. **Standalone Execution**:
   - Single `.html` file using Three.js via CDN (`unpkg.com`), running immediately in any browser with zero compilation.

*Completion criterion*: Functional `.html` file in `prototypes/`, rendering at 60 FPS with responsive orbital controls, layers, and cardinal orientation.

---

## Phase 4 — Sourcing, Local BOM & Quotations (`/quotation-for`)

Translate physical specs into a real-world Bill of Materials with local market pricing:

1. **BOM Decomposition**:
   - Distinguish **Net Dimensions** (finished assembled size) from **Gross Commercial Size** (standard retail rolls, board lengths 3.2m, filament spools 1kg).
   - Calculate cutting waste and material reuse (e.g., solid walls saving mesh area).
2. **Local Market Research (`/quotation-for`)**:
   - Search vendors in the user's region (default Chile: Mercado Libre, Sodimac, Easy, Praver, specialized hardware/electronics suppliers).
   - Collect 3 options per core item (Best Value, Premium/Industrial, Budget).
3. **Quotation Dashboard (`prototypes/[project]_cotizacion.html`)**:
   - Built with **Dual-Theme Pattern**: default dark glassmorphic canvas (`#070b14`), high-contrast text, clear pricing tables.
   - Sourcing summary: total investment, vendor links, availability, and lead times.
   - Interactive cutting plan showing how to divide commercial stock with minimal waste.
4. **Commercial Product Scaling (`/business-implementation-plan`)**:
   - If the project is intended for commercial sale or batch production, trigger `/business-implementation-plan` to calculate unit economics, margins, assembly labour, and scaling roadmap.

*Completion criterion*: Quotation report generated in `prototypes/` with 3 vetted options per critical component, real prices, and a validated cutting plan.

---

## Phase 5 — Living Assembly Manual & Agile Evolution (`/generate-html-doc` + `/agile-prototype`)

Transform the project into an actionable, field-ready construction and assembly guide:

### Step 5.1: Agile Prototyping Roadmap (`/agile-prototype`)
Chart the evolution into **Marks**:
- **MKI**: Minimum viable prototype / structural bench test.
- **MKII**: Field installation with real sensors, plants, or live loads.
- **MKIII**: Automated, finished production build.
Record decisions and milestones in `docs/version_log.md`.

### Step 5.2: Master Assembly Guide (`prototypes/[project]_manual.html`)
Generate using `/generate-html-doc` with the following mandatory sections:
1. **Top Header Bar with Direct Cross-Links**: Sticky header (`.top-bar`) with branding, project subtitle, theme switcher, and direct action buttons linking to the 3D viewer and quotation dashboard.
2. **Executive Blueprint & Metrics**: Scope, dimensions, weights, budget, and direct links.
3. **Material & Hardware BOM**: Complete itemized inventory with hardware specifications.
4. **Tooling & PPE (EPP) Safety**: Personal protection, necessary power tools, calibration gear.
5. **Step-by-Step Procedural Flowchart**: Sequential numbered phases (e.g., Phase 1: Foundation/Chassis $\to$ Phase 2: Uprights $\to$ Phase 3: Roof $\to$ Phase 4: Enclosures/Electronics).
6. **Quality Assurance (QA) Checklist**: Tolerance limits, squareness verification, torque, water tightness, electrical continuity.
7. **Living Registry / Version Log**: Changelog for field adaptations, maintenance schedules, and subsequent Marks.
8. **Dual-Theme Engine**:
   - Dark glassmorphic default on screen (`#070b14`).
   - Visible persistent toggle: `☀️ Modo Claro / 🌙 Modo Noche`.
   - Strict `@media print` isolation: `#ffffff` canvas, black ink, no shadows, header toolbars hidden for zero-waste paper printing.

*Completion criterion*: Self-contained HTML manual in `prototypes/` verified with working theme toggle, direct links to sibling deliverables, and print preview.

---

## Phase 6 — Standardized Interconnected Header & Project Suite Launch

Connect all generated artifacts into a unified project suite. Every generated HTML document (`[project]_3d.html`, `[project]_cotizacion.html`, `[project]_manual.html`) must feature the standardized **Top Navigation Header (`.top-bar`)** with direct action links to all sibling files:

```html
<!-- Top Navigation Bar (Mandatory Standard for All Project HTML Deliverables) -->
<header class="top-bar no-print">
  <div class="brand">
    <div class="brand-icon">🌿</div>
    <div>
      <div class="brand-title">[Nombre del Proyecto / Tipo de Documento]</div>
      <div class="brand-subtitle">[Subtítulo Descriptivo • Ubicación / Especificación]</div>
    </div>
  </div>
  <div class="top-actions">
    <button class="btn-action theme-toggle" id="btn-theme-toggle" onclick="toggleTheme()">
      ☀️ Modo Claro
    </button>
    <a href="[project]_manual.html" class="btn-action" target="_blank">
      📖 Instructivo de Construcción
    </a>
    <a href="[project]_cotizacion.html" class="btn-action" target="_blank">
      📊 Cotización & Despiece
    </a>
    <a href="[project]_3d.html" class="btn-action primary" target="_blank">
      🕶️ Abrir Visor 3D Interactivo
    </a>
    <button class="btn-action" onclick="window.print()">
      🖨️ Imprimir PDF
    </button>
  </div>
</header>
```

Present the final project overview to the user with clickable `file://` links to all deliverables.

---

## Progressive Disclosure & Reference Guides

For deep domain matrices, structural checklists, and IoT hardware templates:
- [WORKFLOW-MATRIX.md](references/WORKFLOW-MATRIX.md) — Step-by-step skill orchestration checklist for physical structures and IoT prototypes.
- [PHYSICAL-CHECKLIST.md](references/PHYSICAL-CHECKLIST.md) — Structural wind/load tolerances, ballast formulas, and outdoor hardware specs.
