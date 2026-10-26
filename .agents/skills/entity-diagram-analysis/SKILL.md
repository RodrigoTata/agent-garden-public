---
name: entity-diagram-analysis
description: Genera diagramas Entidad-Relación en HTML interactivo separados por regiones para aislar el análisis y produce un resumen de arquitectura. Usar cuando el usuario pida diagramas de entidades, modelo ER interactivo, arquitectura de datos o mencione "entity-diagram-analysis".
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Entity Diagram Analysis

## Objective
Analyze a repository to extract database entities, their attributes (with data types), and their relationships. Divide the database into independent **regions** based on the repository's directory structure (modules). Output two artifacts:
1. A single HTML file containing a global ER diagram followed by isolated Mermaid diagrams for each region.
2. A Markdown document (`architecture-summary.md`) divided into a high-level narrative explanation and a highly technical deep-dive section for engineers and LLM agents.

## Steps

1. **Scan the Directory Structure**
   - Identify the primary application code directory (e.g., `src/`).
   - Treat each first-level subdirectory (e.g., `src/cultivo`, `src/usuario`, `src/dispensacion`) as an independent **region**.
   - Find all database model files (e.g., `.entity.ts`, `schema.prisma`) within each region.
   - *Completion criterion:* Every database model file in the repository is mapped to a specific region.

2. **Extract Entities, Attributes, and Types**
   - For each model file, parse the entity name.
   - Extract all columns/properties, identifying their name and exact data type (e.g., `int`, `varchar`, `date`, `float`, `boolean`).
   - Extract all relationships (e.g., ManyToOne, OneToMany, Foreign Keys).
   - *Completion criterion:* All models are fully parsed in memory with their data types and relationships intact.

3. **Generate Mermaid Diagrams**
   - **Global Diagram:** Generate one unified `erDiagram` representing the entire database schema to show high-level connectivity.
   - **Regional Diagrams:** For each region, create an isolated `erDiagram` block. Include the full definition (attributes and types) for internal entities. If a relationship points outside the region, represent the external entity as a simplified stub (name only, no attributes).
   - *Completion criterion:* A valid Mermaid string exists for the global view and for every identified region.

4. **Construct the HTML Output**
   - Embed the generated Mermaid diagrams into a single HTML document.
   - Use an `<h1>` for the global diagram and `<h2>` for each region.
   - Wrap each Mermaid string in `<pre class="mermaid">` tags.
   - Include the Mermaid JavaScript CDN block to auto-render the diagrams.
   - Use the `write_to_file` tool to save the output as `entity-diagrams.html`.
   - *Completion criterion:* The HTML file provides a global overview followed by isolated views for each module.

5. **Generate Architecture Documentation (.md)**
   - Create a markdown file named `architecture-summary.md`.
   - **Part A (Narrative):** Write a concise, business-focused narrative (1-3 minute read) explaining the system's purpose, the core domain modules, and how they provide value. Avoid technical jargon.
   - **Part B (Technical/LLM):** Write a dense, technical deep-dive. Detail the ORM patterns, key foreign key relationships, data types, and potential architectural coupling risks between regions.
   - Use the `write_to_file` tool to save the document.
   - *Completion criterion:* The markdown file is saved with both the narrative section and the technical section fully populated.

## Failure Modes
- **Spaghetti Diagram:** Failing to provide a logical hierarchy in the HTML. Prevent this by prioritizing the global view at the top, followed by cleanly separated regional sections.
- **Missing External Keys:** Dropping relationships to other regions entirely. Fix this by including the external entity as an empty stub inside the current region's diagram.
- **Overly Technical Intro:** Writing the narrative section for developers rather than business stakeholders. Keep Part A focused on domain outcomes and system value.
