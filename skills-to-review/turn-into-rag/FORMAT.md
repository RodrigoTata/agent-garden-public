# File formats

## Section file (`NN-<topic>.md`)

```markdown
---
source_id: industrial-cannabis-cultivation
source: "Industrial Cannabis Cultivation — J. Grower (2021)"
section: "Ch. 4 › Lighting"
locator: "pp. 87–121"
topics: [lighting, ppfd, dli, photoperiod, co2]
---

# Lighting — Industrial Cannabis Cultivation

## PPFD targets for cannabis by growth stage

*Answers:* How much light does cannabis need in flower? What PPFD suits clones?

| Stage | PPFD (µmol/m²/s) | Photoperiod |
|---|---|---|
| Clones | 100–200 | 18/6 |
| Vegetative | 400–600 | 18/6 |
| Flowering | 900–1100 | 12/12 |

(p. 92)

- Above 1000 PPFD, raise CO₂ to 1200 ppm or the extra light is wasted (p. 94).

> Note: the book's values assume HPS fixtures; it does not discuss LED equivalence.
```

- **H1**: `<section> — <source short title>`.
- **H2** is one retrievable chunk of roughly 150–600 words. Name both the subject and the aspect, so the heading alone says what the chunk holds: "PPFD targets for cannabis by growth stage", not "Targets" or "Part 2". Split an H2 that runs past 600 words; merge a stub under about 80 words into a neighbour.
- **`*Answers:*`** goes under every H2: 1–3 questions a user would actually ask that this chunk answers. Retrieval matches a question to another question better than to a statement.
- Use bullets, tables and numbered steps. Use prose only for mechanisms.
- Put a **locator** at the end of each claim or group of bullets: `(p. 92)`, `(pp. 92–94)`, `[00:12:34]`, `(slide 4)`, `(Fig. 4.2, p. 95)`. Unpaginated sources (web, Word, EPUB) rely on the frontmatter `locator`; add `(§ <heading>)` only when citing a different section.
- Nothing inside an H2 may point outside it. Instead of "this method" or "as above", name the thing again (orphan test).
- When a figure or table existed only as an image, transcribe its data into a Markdown table and cite the figure.
- `topics`: 3–8 lowercase search keywords, including abbreviations (`ppfd`) and, where both are common, their expansions.

## Overview (`00-overview.md`)

```markdown
---
source_id: industrial-cannabis-cultivation
title: "Industrial Cannabis Cultivation"
authors: ["J. Grower"]
date: 2021
type: book            # book | paper | article | video | audio | manual | standard
origin: "C:/books/icc.pdf"
language: en
distilled: 2026-10-17
coverage: "Chapters 1–14; appendices B–C skipped (supplier lists)"
topics: [cannabis, indoor cultivation, climate, lighting, fertigation, ipm]
---

# Industrial Cannabis Cultivation — overview

<2–4 sentences: what the source covers, for whom, its approach, and its limits (edition, region, date, bias).>

## Key takeaways

- Flowering rooms run at 900–1100 PPFD on 12/12 with CO₂ at 1200 ppm → [04-lighting.md](04-lighting.md)

## Map

| File | Covers |
|---|---|
| [01-climate.md](01-climate.md) | Temperature, RH and VPD targets per stage; HVAC sizing |

## Caveats

- <limits of edition, date or region; things the source leaves out or that look outdated>
```

## Glossary (`glossary.md`)

```markdown
# Glossary — Industrial Cannabis Cultivation

**DLI (daily light integral)** — total photosynthetic light per day, in mol/m²/d; DLI = PPFD × hours × 0.0036 (p. 90) · [04-lighting.md](04-lighting.md)
```

One line per term, alphabetical, with the definition as the source gives it. Each line becomes its own chunk on export, so it has to make sense alone.

## Single file (`<slug>.md`, for 1-row sources)

```markdown
---
<the overview frontmatter>
---

# <Title>

<2–4 sentence scope>

## Key takeaways

- <3–7 bullets>

## <Topic sections, each an H2 as in a section file>

## Glossary

**Term** — definition (locator)
```

## Index (`knowledge/INDEX.md`)

```markdown
# Knowledge index

- [Industrial Cannabis Cultivation](industrial-cannabis-cultivation/00-overview.md) — book, J. Grower 2021 · indoor commercial cultivation: climate, lighting, fertigation, IPM, harvest
- [Dialing in VPD for flowering](dialing-in-vpd-for-flowering.md) — article, growsite.com 2024 · VPD targets per growth stage
```

Each line links to the source's entry file and gives its type, author or site, and year, followed by the topics someone would search for.

## Ledger rows

A row starts as `todo` and becomes either `done` (with its distilled word count) or `skipped — <reason>`. Edit only the last two cells.
