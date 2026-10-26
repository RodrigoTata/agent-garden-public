---
name: interior-exterior-designer
description: Designs renovated interiors and exteriors from photos of a space's current state. It surveys the photos with computer vision, grills the owner, and delivers a buyable scheme (real retail products with prices, analog and smart variants, ergonomics checks, plants), a 3D twin, photoreal renders and a presentation. Use when the user shares photos of a room, home, balcony, terrace or garden and wants it redesigned, renovated, furnished or decorated; when the user wants an AI interior designer or a webapp that does this; or when another skill needs an interior or exterior design.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Interior & Exterior Designer

An **orchestrator**: it runs the design process and hands each specialised job to an existing AgentGarden skill. It writes no viewer, quotation engine or document template of its own.

Five terms run the process:

- **Survey**: what the space is *today*, read from photos. Every measurement carries a source.
- **Brief**: the owner's decisions, settled by grilling. Nothing about taste, budget or people is assumed.
- **Scheme**: the proposed design per room or zone, with layout, items, palette, variants and checks.
- **Buyable**: every item in a scheme is a real retail product with store, price, link and the date the price was seen. Custom-built pieces only when the brief asks for them.
- **Paint**: photorealism is painted over a geometry reference (the current photo or a 3D twin view). The AI never decides where a wall, window or product goes; the scheme does.

`<skill-dir>` is the folder holding this file.

## Contract (for callers)

Another agent or skill can call this one with:

| Input | Required | Notes |
|---|---|---|
| Photos of the current state | yes | Per room/zone, ideally one from each corner (see Step 1) |
| Scope | yes | Which rooms or zones, interior and/or exterior |
| Plan, measurements, budget, store list | no | Each one supplied shortens the grilling |
| Settled decisions | no | Any decision already made is written into the brief and not asked again |
| Mode | no | `session` (default) or `webapp` |

It writes everything to `design/` in the active project (or where the caller says):

```
design/
├── photos/          originals, never edited (renamed <room>-<nn>.jpg)
├── survey.md        Step 2
├── brief.md         Step 3
├── scheme.md        Steps 4-5: one section per room/zone, the buyable list, the checks
├── twin/            Step 6: interactive 3D viewers, one per room or per home
├── renders/         Step 7: painted images, prompt packs, render-log.md
└── presentation.html  Step 8
```

Deliverables are written in the owner's language; the files above keep their names.

## Branches

| Branch | When | Path |
|---|---|---|
| **Session** (default) | Design a real space now, inside this conversation | Steps 1–9 |
| **Exterior** | The scope includes a balcony, terrace, patio, garden, roof or facade | Same steps; for those zones [EXTERIOR.md](EXTERIOR.md) replaces the interior rules |
| **Webapp** | The owner wants a standalone app that does this process for anyone | Read [WEBAPP.md](WEBAPP.md) and hand off to `/to-spec`; this skill's steps become the app's spec |

A request can take two branches (a home with a balcony is Session + Exterior). Webapp starts only when the owner asks for an app; designing their own home never requires building one.

## Steps

### 1. Intake

Collect the photos and the scope. Copy the photos into `design/photos/` as `<room>-<nn>.jpg`, keeping the originals untouched.

For each room or zone you need: one photo from each corner, the window and door walls straight-on, and close-ups of fixed points (water inlets and drains, the electrical panel, outlets, gas, radiators). For measuring, one anchor per photo: a tape measure on the wall, or an object of known size (see `/3d-scanner` › FOTOS.md). Ask for missing shots in one message. If the owner can't take them, continue: those walls become `supuesto` (assumed) in the survey.

**Done when** every room/zone in scope has photos filed, and every missing view is either requested or recorded as a gap.

### 2. Survey

Read every photo with vision following [SURVEY.md](SURVEY.md), and write `design/survey.md`. Measurements use the source tags and measuring tools of `/3d-scanner` (`medido`, `foto ✓`, `foto`, `catálogo`, `supuesto`, with its `lupa`/`rectificar` scripts). Run its Steps 2–3 for any dimension that a later fit, ergonomics check or purchase depends on.

**Done when** every room/zone has every SURVEY.md field filled or marked unknown, every dimension has a source tag, and the "ask the owner" list is ready for Step 3.

### 3. Brief

Run `/grilling` over the design tree in [BRIEF.md](BRIEF.md). Fold the survey's "ask the owner" list into the first rounds. Skip any decision the caller already settled; mark it "given" in the brief. Questions go as plain text with your recommended answer, never as clickable option buttons.

**Done when** the grilling frontier is empty, `design/brief.md` records every decision, and the owner has confirmed the brief.

### 4. Scheme

Design each room/zone with [DESIGN.md](DESIGN.md) (or EXTERIOR.md for exterior zones), and write it into `design/scheme.md` using DESIGN.md's template:

1. Layout: each item's position, footprint and clearances in mm, drawn from survey dimensions.
2. Item specs: category, maximum dimensions, style, material, budget line. These are specs, not products yet.
3. Palette and lighting layers.
4. Analog and Smart variants over the same layout.
5. Plant(s), filtered by light, humidity and pets.
6. The ergonomics check table, every rule measured.

**Done when** every room/zone has all six parts, and every ergonomics rule shows a measured value and pass/fail. Failures are either fixed or accepted by the owner with a reason.

### 5. Buy

Turn every item spec into a buyable product with `/quotation-for`, restricted to the stores in the brief (default Chile: Sodimac, Easy, IKEA, Falabella, Paris, Ripley, MercadoLibre). For each spec it returns 3 options and a recommendation. Record the chosen one in the scheme's buyable list: store, product name, price CLP, link, real dimensions, date seen.

Then re-check fit with the real dimensions. A product larger than its spec goes back to Step 4 for that room: rerun the ergonomics table there.

**Done when** every item is either buyable with all six fields filled or flagged "not found" with the closest alternative, and the per-room and total sums are written for both variants.

### 6. Twin

Build a 3D digital twin of each room whose layout changes or whose fit is tight, with `/interactive-3d-structure`. Use survey dimensions for the shell and real product dimensions for items. Put each item's store and price in its `nota` and give each variant its own layer. Use `dentroDe` for items that must fit inside niches.

Skip the twin for rooms with only finish and decor changes (paint, textiles, lamps, plants), and say so in the scheme.

**Done when** each twin's `verify.mjs` prints `VERDE`, or a skipped twin has its reason written in the scheme.

### 7. Paint

Produce the "after" images following [PAINT.md](PAINT.md): one fresh paint pass per view from its geometry reference (the survey photo, or a twin view when the layout changes), with the chosen products' photos as references. Log every image in `design/renders/render-log.md`.

If no image-generation tool or API is available in this environment, write PAINT.md's prompt pack for each view instead, so the owner (or the webapp later) can run it.

**Done when** every view in scope has either a painted image with its log row or a complete prompt pack, and every painted image passed PAINT.md's geometry check.

### 8. Present

Build `design/presentation.html` with `/generate-html-doc` (type *documento mixto*). Follow this order:
1. Whole-home view (plan or twin).
2. Per room: before/after with a comparison slider, a headline, why it works, the Analog/Smart toggle, an ergonomics badge.
3. Buyable list with per-room and total prices for both variants, links and dates seen.
4. Plants, works that need an installer, and notes. Painted decor is marked "illustrative" unless it comes from the buyable list.

**Done when** every room in the scheme appears with its images (or prompt pack), totals equal the sum of the buyable list, every link opens, and the file renders in a browser.

### 9. Review and iterate

Report the files, open warnings, "not found" items and next options. Changes the owner asks for go back to the earliest affected step. Earlier images and versions move to `design/archive/` and are never overwritten.

Next options to offer, only the ones that apply:
- `/finantial-analysis`: compare variants or phases against a budget.
- `/agile-prototype`: plan the works in stages (Marks).
- `/start-a-proyect`: built pieces such as shelves, a pergola or planters.
- The Exterior branch, if exterior zones were left out.
- The Webapp branch.

**Done when** the owner has the report and every requested change has gone through its steps again or is listed as pending.
