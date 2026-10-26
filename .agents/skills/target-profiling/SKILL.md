---
name: target-profiling
description: Profile individuals, public officials, or persons of interest (targets/POIs) using intelligence agency tradecraft (OSINT, Intelligence Cycle, Assessment of Persons, Link Analysis). Use when the user wants to profile a target, build an intelligence dossier, investigate public officials, or mentions "target-profiling", "intel profile", or "perfilado".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Target Profiling

Disciplined persona and target profiling following the intelligence cycle of premier services (CIA, MI6, FSB, Mossad) using open-source intelligence (OSINT).

The leading words are **triangulate**, **doctrine**, and **timestamp**:
- **Triangulate**: No factual claim enters the dossier on a single source. Every milestone, asset, or case must be verified across orthogonal public vectors or explicitly quarantined.
- **Doctrine**: Analysis reconstructs the subject's operating philosophy, decision patterns, and cognitive style strictly from documented precedents, never subjective impressions.
- **Timestamp**: Every political relationship, cabinet counterpart, and institutional post is anchored to the exact live execution date (`YYYY-MM-DD`). Never assume historical incumbents from training priors or past news still hold office.

Deep definitions, the Admiralty rating scale, and behavioral frameworks live in [`references/METHODOLOGY.md`](references/METHODOLOGY.md). The output schema lives in [`references/DOSSIER_TEMPLATE.md`](references/DOSSIER_TEMPLATE.md).

---

## Inter-Skill Coordination

Reach for companion skills when specific workloads arise:

- **Deep statutory/gazette legwork**: Invoke [`research`](../research/SKILL.md) to sweep official gazettes, decrees, and legislative records.
- **Document ingestion**: Invoke [`context-extractor`](../context-extractor/SKILL.md) to parse PDF asset declarations, court rulings, and academic dissertations.
- **Executive HTML briefing**: Invoke [`generate-html-doc`](../generate-html-doc/SKILL.md) to scaffold a dual-theme (dark glassmorphic / clean print) standalone dossier.
- **Network cluster visualization**: Invoke [`entity-diagram-analysis`](../entity-diagram-analysis/SKILL.md) when the subject belongs to a multi-node institutional patronage network.

---

## Steps

### Step 1 — Direction, Temporal Baseline & PIR Specification

Before issuing subject-specific queries, establish the temporal envelope and initialize the Priority Intelligence Requirements (PIRs):

1. **Temporal Baseline**:
   - Record the execution date (`YYYY-MM-DD`).
   - Query and verify the **current sitting Head of State** and statutory counterparts (Minister of Justice, Minister of the Interior, Senate President) *as of today's date*.
   - Never import sitting authorities from pretraining memory. If the execution date falls in a new presidential cycle (e.g., post-March 2026), establish the sitting administration first.
2. **Target Envelope**: Record full legal name, known maternal/paternal surnames, public national ID (if public record), active official post, and jurisdictional boundaries.
3. **PIR Scorecard**: Formulate 4 targeted requirements:
   - **PIR-1 (Escalator & Sponsors)**: Who appointed or promoted them? Which mentors or political blocs accelerated their career?
   - **PIR-2 (Operating Doctrine)**: What are their observable procedural patterns (e.g., punitive threshold, plea settlement appetite, procedural vs. substantive)?
   - **PIR-3 (Network & Faction)**: Who constitutes their inner circle, institutional faction, and adversarial nodes?
   - **PIR-4 (Friction & Vulnerability)**: What appellate reversals, administrative sanctions, ethics complaints, or asset anomalies exist?

**Completion criterion**: Target sheet, verified sitting Head of State/counterparts at current timestamp, and 4 PIRs initialized in working notes before any target-specific search query is executed.

---

### Step 2 — Orthogonal OSINT Harvesting & Triangulation

Harvest intelligence strictly from public-access sources across the 5 collection vectors detailed in [`references/METHODOLOGY.md`](references/METHODOLOGY.md):
- **V1 (State & Regulatory)**: *Diario Oficial*, *Transparencia Activa*, *InfoProbidad* (patrimonial disclosures), statutory decrees.
- **V2 (Judicial & Dockets)**: Court registries, appellate rulings, nomination hearing transcripts, bar associations.
- **V3 (Academic & Intellectual)**: Law reviews, faculty records, theses, published doctrine, citations.
- **V4 (Press & Media Archives)**: Investigative repositories (*CIPER*, national press archives), on-record interviews, press conference recordings.
- **V5 (Institutional Affiliations)**: Judicial/prosecutorial unions, university alumni councils, advisory boards.

**Triangulation & Tenure Rules**:
1. Grade every source and claim using the Admiralty Code (Reliability A–F, Credibility 1–6) from [`references/METHODOLOGY.md`](references/METHODOLOGY.md).
2. Only claims rated **A1 through B2** may be incorporated as established facts.
3. Claims with single-source press mentions (rated B3/C3) must be explicitly flagged as `[UNCORROBORATED REPORT]`.
4. Social media chatter, anonymous posts, or unverified claims must be discarded.
5. **Incumbency Check**: Whenever attributing a title ("ministro", "senador", "subsecretario") to an associate, verify whether that title is *active* or *past* relative to the execution date. All past titles must be labeled with their exact tenure (e.g., *exministro Segpres 2023–2026*).

**Completion criterion**: Every milestone and major case backed by ≥2 sources rated A1–B2, and 100% of mentioned political associates verified for active vs. past tenure.

---

### Step 3 — Behavioral & Cognitive Assessment (CIA Model)

Evaluate the verified record against the CIA Center for Analysis of Personality & Political Behavior framework:

1. **Cognitive & Decision Style**:
   - Classify as *Proceduralist* (strict adherence to formal procedure) vs. *Substantive* (outcome-oriented, activist).
   - Classify risk appetite: *Consensus-seeking institutionalist* vs. *High-risk crusader*.
2. **Motivational Drivers (SMICE)**:
   - Identify primary driver: institutional preservation, peer acclaim, career ladder climb, or ideological crusade.
   - Establish public persona archetype (e.g., The Strict Jurist, The Reformer, The Quiet Bureaucrat).
3. **Crisis & Pressure Response**:
   - Document how the subject responded to historical shocks: appellate overturns, press scrutiny, or executive branch pressure.
4. **Substantive Operating Doctrine**:
   - For legal/judicial targets: threshold for coercive measures (pre-trial detention), disposition toward negotiated outcomes, and degree of control over police investigators.

**Completion criterion**: All 4 behavioral dimensions evaluated with documented case precedents cited. Zero speculative psychologizing without factual grounding.

---

### Step 4 — Link Analysis & Friction Matrix

Map the target's relational dependencies and points of exposure:

1. **Sociogram (Network Map)**:
   - Identify patrons (sponsors who enabled upward mobility), lieutenants (trusted staff moving across assignments), factional allies, and confirmed adversaries.
   - Explicitly annotate each node with their verified status at the execution timestamp (e.g., *exministro*, *senador en ejercicio*, *exdecano*).
2. **Friction & Vulnerability Audit**:
   - Document overturned cases, public controversies, official reprimands, or declared commercial/familial conflicts of interest.
   - If no recorded friction exists in public records, record `NO ADVERSE PUBLIC FINDINGS`.

**Completion criterion**: Sociogram table populated with verified tenure-annotated relationships and friction audit completed with primary source citations.

---

### Step 5 — Dossier Assembly & Delivery

Assemble the final deliverable using [`references/DOSSIER_TEMPLATE.md`](references/DOSSIER_TEMPLATE.md):

1. **Executive BLUF (Bottom Line Up Front)**:
   - Draft a dense, 2–3 paragraph summary capturing operational leverage, behavioral archetype, decision doctrine, and primary vulnerability in the context of the sitting administration.
2. **Dossier Sections**:
   - Embed Target ID, PIR Scorecard, Career Chronology, Behavioral Assessment, Operating Doctrine, Sociogram, Friction Matrix, and Admiralty Sources Table.
3. **Deliverable Format**:
   - Standard: Save as `docs/intelligence/dossier-[target-surname].md`.
   - Executive Brief: If requested, run [`generate-html-doc`](../generate-html-doc/SKILL.md) to produce a standalone dual-theme HTML briefing.

**Completion criterion**: Dossier file saved, containing all template sections, with 100% of factual assertions traceable to the Admiralty Sources Table and zero anachronistic incumbency labels.

---

## Failure Modes to Avoid

- **Temporal Drift / Anachronistic Incumbency**: Assuming political figures, ministers, or associates mentioned in historical press archives still occupy those posts today. Any statement claiming an entity is "current" without verifying active tenure at the execution timestamp fails the audit.
- **Premature Completion**: Writing a profile after glancing at news articles. The completion criteria demand multi-vector triangulation across official gazettes and transparency portals.
- **Homonym Pollution**: Conflating the target with a person sharing the same name. Always cross-reference full legal maternal/paternal names and professions in official registries.
- **Unanchored Speculation**: Diagnosing psychological traits without citing observable actions or documented precedents.
- **Gossip Infiltration**: Treating unverified forum commentary or anonymous allegations as intelligence. Enforce the A1–B2 Admiralty threshold unconditionally.
- **No-Op Generalities**: Stating "the subject is professional and hardworking." Every assessment must declare an observable operational style backed by evidence.
