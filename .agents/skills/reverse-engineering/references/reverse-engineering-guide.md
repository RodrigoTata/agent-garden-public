# Reference Guide: Reverse Engineering Methodology

> Primary reference for the `reverse-engineering` skill. Defines the formal 4-phase methodology for deconstructing physical products and software services to inform new product development.

---

## 1. Core Principles of Reverse Engineering

Reverse engineering is the process of extracting knowledge or design information from anything human-made and re-layering that knowledge into a high-level abstraction to guide new development.

### The 4 Methodology Phases

```
1. Black Box Analysis   --> Inputs/Outputs, UX, Outer Spec
2. Teardown & Deconstruct --> Disassembly, Materials BOM / Tech Stack
3. Trade-Off Analysis     --> Pros, Cons, Cost Drivers, Failure Modes
4. Re-Synthesis          --> Actionable Blueprint / Spec for Redesign
```

---

## 2. Phase Breakdown

### Phase 1: Black Box Analysis
Analyze the target product or service strictly from the outside without opening or decompiling:
- **Inputs & Outputs:** What goes in, what comes out (voltage, data, raw materials, user actions).
- **External Interfaces:** Connectors, buttons, API endpoints, UI screens.
- **Observed Performance:** Operating limits, response times, thermal output, power draw.

### Phase 2: Teardown & Functional Decomposition

#### For Physical Products (Manufacturing / Hardware)
- **BOM (Bill of Materials) Teardown:** List every part, fastener, PCB component, and sensor.
- **Materials Identification:** Plastics (PETG, ABS, PC, TPU), metals (Aluminum 6061, Brass, Stainless 304), board finishes (ENIG, HASL).
- **Manufacturing Process Inference:** Injection molding (draft angles, parting lines), CNC machining, additive 3D printing, SMD PCB assembly.
- **Isolated Airpath & Safety Audit:** Inspect thermal boundaries, food-contact safety, electrical insulation, and lead-free compliance.

#### For Software Products & Services (Digital / APIs)
- **Architecture Extraction:** Client-side framework, backend runtime, database type, communication protocols (REST, GraphQL, MQTT, WebSockets).
- **Data Flow & Schema Inference:** Payload shapes, authentication mechanisms, state management strategy.
- **Dependency Audit:** Third-party libraries, SDKs, external cloud services.

### Phase 3: Trade-Off & Failure Mode Analysis
Evaluate what the original creators got right and where they compromised:
- **Pros (What to emulate):** Clever mechanisms, cost-efficient parts, intuitive UX choices.
- **Cons (What to avoid):** Fragile components, high BOM cost, thermal bottlenecks, security flaws.
- **Failure Modes:** Known ways the product degrades or breaks over time.

### Phase 4: Re-Synthesis (Redesign Blueprint)
Convert findings into an actionable specification for our own development:
- **Emulate:** Features and choices that must be preserved.
- **Improve:** Known pain points that our redesign will fix.
- **Cost Target:** Target BOM or Tech Stack cost based on the deconstruction.
- **Handoff:** Ready to feed into `/agile-prototype`, `/to-spec`, or `/wayfinder`.

---

## Sources & Standards

- Wikipedia: *Reverse Engineering* (Information extraction, modeling, review).
- Wikipedia: *Black Box* (Input/output functional analysis).
- Chikofsky & Cross: *Reverse Engineering and Design Recovery* (IEEE Software).
