---
name: generate-html-doc
description: "Genera documentos HTML completos: instructivos, guías explicativas, referencias técnicas, planes de acción, manuales, y cualquier documento estructurado. Use when the user asks to generate an HTML document, create an instructivo, producir una guía, or build any printable/shareable structured document in HTML."
disable-model-invocation: false
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# generate-html-doc

**Scaffold** a complete, print-ready HTML document from a description, data, or an existing document.  
**Scaffold** = build the full HTML shell with the design system already wired, so the agent only fills in content.

The leading word is **scaffold**: every run follows the same deterministic structure — design system first, then sections in order, then polish. This is not "write some HTML"; it is instantiating a known pattern from a template.

---

## Steps

### Step 1 — Classify the document

Identify the **document type** from the request. Types share the same design system but differ in which content blocks they use:

| Type | Leading blocks |
|---|---|
| **Instructivo** (procedural) | Flowchart steps + callout boxes + numbered protocol |
| **Guía explicativa** (conceptual) | Section prose + grid cards + tables + callouts |
| **Tabla de referencia** | Large data table(s) + brief prose + callouts |
| **Plan / cronograma** | Timeline flowchart + table + alerts |
| **Documento mixto** | Any combination of the above |

If the request is ambiguous, pick the type that fits the majority of the content.

**Completion criterion:** type is identified, content blocks selected. Proceed only after this is clear.

---

### Step 2 — Gather content

Extract from the user's request (or attached document):

1. **Title** and optional subtitle
2. **Metadata row**: date, author, version, location, or any domain-specific fields (up to 4 fields, in a 2x2 grid)
3. **Section list**: the main numbered sections and their purpose
4. **Primary color**: if the user specifies a domain or theme, pick a harmonious primary color for the design system. Defaults: `#1e6ba8` (blue, technical docs), `#2e7d32` (green, agro/nature), `#6d3b8c` (purple, creative), `#b34700` (amber, operations). The dark base is always `#1a1a2e`.
5. **Language**: detect from content; set `lang` attribute accordingly.

**Completion criterion:** all 5 items above are resolved. If primary color is unspecified and no domain is clear, default to `#1e6ba8`.

---

### Step 3 — Scaffold the HTML

Produce **one self-contained `.html` file**. No external CSS files, no external JS files — everything is inline. The file must open correctly offline.

#### 3a. Design system (required, always)

Wire the full CSS design system from `design-system.md` (sibling file in this skill folder) into the `<style>` tag.  
Replace `VAR_PRIMARY` with the chosen primary color throughout.  
Replace `VAR_PRIMARY_DARK` with a 15% darker variant.

**Dual-Theme Engine:** The design system implements **Modo Noche (Dark Glassmorphic)** as the default screen experience (rich dark slate canvas `#070b14`, glassmorphism, glowing accents) and **Modo Claro** (`body.theme-light`) for daytime reading. Physical printing / PDF export (`@media print`) is strictly isolated to force pure white background and dark text to avoid ink waste.

#### 3b. Content blocks — usage rules

Use blocks only when they serve the content. Do not include a block just to fill space.

| Block | When to use |
|---|---|
| `div.flow-step` | Sequential steps where order and completion matter |
| `div.callout` | Critical rules, warnings, tips. Use `.warning` or `.success` modifier as needed |
| `div.grid-2` + `div.card` | Two parallel concepts, pros/cons, side-by-side comparisons |
| `table` inside `.table-container` | Structured data with 3+ columns or 5+ rows |
| `span.badge` | Short status labels inside cells or step headers |

#### 3c. Structure

```
DOCTYPE -> head (meta, title, style) -> body
  |- header.top-bar.no-print (Interconnected Project Suite Header)
  |    |- div.brand (icon, title, subtitle)
  |    +- div.top-actions
  |         |- button#btn-theme-toggle (toggles Modo Noche / Modo Claro)
  |         |- a.btn-action (direct links to sibling files: Visor 3D, Cotización, Docs)
  |         +- button.btn-action (window.print PDF)
  +- div.document
       |- div.doc-header  (title, subtitle, div.doc-meta)
       |- h2 1. ...  <- sections, numbered, in order
       |     +- blocks
       |- h2 2. ...
       |     +- blocks
       +- div.doc-footer
  +- script (theme toggle logic with localStorage persistence)
```

**Page breaks:** insert `<div class="page-break"></div>` before any section that should begin on a new PDF page (typically after the first dense table or after section 2).

**Completion criterion:** every section has at least one content block (prose counts). No section is empty.

---

### Step 4 — Polish

Before delivering, verify:

- [ ] `html lang="..."` matches the content language
- [ ] `title` tag matches the document title
- [ ] Primary color is applied consistently (header border, h3, flow-step-number, badge-primary, print-btn gradient)
- [ ] Dual-Theme engine is wired: Dark mode glassmorphic by default, Light mode toggle available
- [ ] Theme toggle button exists (`#btn-theme-toggle`) and persists state in `localStorage`
- [ ] Print button exists with `class="no-print"`
- [ ] `@media print` block hides `.no-print`, removes dark backgrounds and forces clean white paper
- [ ] At least one `div.callout` exists (even a tip counts)
- [ ] Footer contains document title and a date or version reference
- [ ] The file has no broken external references (only Google Fonts is allowed as external)

**Completion criterion:** all checklist items are checked. Deliver the file.

---

## Output

Write the file to a sensible location:
- If the request is tied to a specific repo/project, write it in that project's `docs/` or `Auxiliar/` directory
- If no location is specified, write it to the conversation artifacts directory
- Filename: `slug-of-title.html` (lowercase, hyphens)

After writing the file, report: file path (as a clickable link), document type identified, primary color used, and sections generated.

---

## Failure modes to avoid

- **Sediment**: do not copy unused CSS classes from the design system into the file. If a block type is not used in this document, its CSS can be omitted.
- **No-op sections**: do not create sections just to match a generic template. Every h2 must have real content.
- **Premature completion**: do not deliver after Step 3a. The polish checklist in Step 4 is mandatory.
- **Color inconsistency**: if the user's topic clearly has a domain (agro = green, medical = blue-teal, legal = dark navy), align the primary color. A mismatch is jarring.
