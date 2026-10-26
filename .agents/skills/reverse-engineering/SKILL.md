---
name: reverse-engineering
description: Perform a systematic reverse engineering analysis of a physical product or software service, deconstructing its BOM, architecture, materials, trade-offs, and manufacturing to guide new development. Use when the user asks to reverse engineer, deconstruct a product, analyze how a product/service is built, perform a teardown, or mentions "reverse engineering", "desarmar producto", or "ingeniería inversa".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

A target product or service has arrived — physical hardware or digital software. This skill systematic deconstructs it using the 4-phase reverse engineering methodology to extract its design principles, materials, architecture, and trade-offs, producing an actionable report to guide a new redesign.

The leading word is **Deconstruct** — to break down a product into its fundamental components, materials, data flows, and mechanisms to inform a new design.

## 1. Identify Target & Domain

Determine whether the target is a **Physical Product** (hardware, electronics, manufacturing) or a **Software Service** (web/mobile app, API, protocol).

Run `/research` to gather primary sources — teardown videos, patents, datasheets, API docs, teardown blog posts, or open-source equivalents.

**Completion criterion**: Target identified, domain classified (Physical vs. Software), and primary research sources gathered.

## 2. Execute Phase 1 — Black Box Analysis

Analyze the target purely from the outside:

- **Inputs & Outputs**: Power, signals, raw materials, data payloads, user actions.
- **Interfaces**: Connectors, UI screens, API endpoints, physical buttons, mounting points.
- **Performance Envelope**: Operating limits, thermal output, power draw, latency, or yield.

**Completion criterion**: Documented Black Box summary describing all inputs, outputs, and observed performance limits.

## 3. Execute Phase 2 — Teardown & Functional Decomposition

Deconstruct the target into its constituent parts:

### For Physical Products
- **BOM Teardown**: Deconstruct the assembly into parts — structural housing, fasteners, PCBs, microcontrollers, sensors, actuators.
- **Materials Identification**: Specify exact materials (e.g., PETG, Aluminum 6061, Brass, Lead-Free solder, Silicone).
- **Manufacturing Process**: Infer manufacturing methods (Injection molding, CNC machining, FDM/SLA 3D printing, SMD PCB assembly).

### For Software Services
- **Tech Stack Breakdown**: Client framework, backend runtime, database, messaging protocols (REST, MQTT, WebSockets).
- **Data Flow & Schema**: Deconstruct payload shapes, authentication flows, and state management.
- **Dependency Audit**: List key third-party libraries, SDKs, and cloud services.

**Completion criterion**: A complete BOM (for hardware) or Tech Stack matrix (for software) detailing all components and manufacturing/architectural methods.

## 4. Execute Phase 3 — Trade-Off & Failure Analysis

Evaluate the original design choices:

- **Pros (To Emulate)**: Clever mechanisms, cost-effective part choices, exceptional UX.
- **Cons (To Avoid)**: Fragile materials, expensive BOM items, high latency, poor repairability.
- **Failure Modes**: How the product fails over time (thermal stress, wear, security bugs).

**Completion criterion**: Bulleted trade-off matrix highlighting what to emulate and what to fix in the redesign.

## 5. Execute Phase 4 — Re-Synthesis Report

Compile all findings into a structured report saved as `reverse_engineering_report.md` in the project's `docs/` or `.dev/` directory:

```markdown
# Reverse Engineering Report: [Target Name]

## 1. Overview & Black Box Analysis
- **Domain:** [Physical / Software / Hybrid]
- **Primary Function:** [Summary]
- **Inputs & Outputs:** [Table or List]

## 2. Teardown & Decomposition
- **BOM / Tech Stack:** [Detailed Component Table]
- **Materials & Manufacturing / Architecture:** [Analysis]

## 3. Trade-Off Matrix
- **Strengths (Emulate):** [List]
- **Weaknesses (Fix):** [List]
- **Cost Driver Analysis:** [Key expensive parts/services]

## 4. Redesign Blueprint & Handoff
- **Key Takeaways for Our Product:** [Actionable guidelines]
- **Target Cost Envelope:** [Estimated BOM or hosting cost]
- **Next Skill Handoff:** [e.g., /agile-prototype, /to-spec, or /wayfinder]
```

**Completion criterion**: `reverse_engineering_report.md` saved with all 4 phases complete, ready for handoff to prototyping or spec skills.

---

## Domain-specific guidance

Consult [`references/reverse-engineering-guide.md`](references/reverse-engineering-guide.md) for the full methodology reference, phase details, and source citations.
