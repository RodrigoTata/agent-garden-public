# Webapp branch — blueprint

The owner wants a standalone web app that runs this skill's process for anyone. This file is a **blueprint for the spec, not code**. The build goes through the usual skills:

1. `/grill-me-rg` on the open decisions at the end of this file.
2. `/to-spec` writes the PRD from this blueprint plus the answers.
3. `/agile-prototype` charts the Marks; MKI is defined below.
4. `/to-tickets` → `/tdd` (or `/execute`) builds it.

The skill's own files stay the single source of truth for the app's behaviour. The app's prompts load SURVEY.md, BRIEF.md, DESIGN.md, EXTERIOR.md and PAINT.md at startup instead of copying their rules into code. Editing the skill then changes the app.

## What the app does (the skill's steps as screens)

| Screen | Skill step | What happens |
|---|---|---|
| 1. Upload | Intake | Drop photos per room/zone, choose the scope, optional plan and measurements |
| 2. Survey | Survey | A vision model reads the photos and returns the survey as structured JSON (SURVEY.md fields + source tags). The owner edits or confirms each field and types the measurements it asks for |
| 3. Interview | Brief | One question at a time with a recommended answer and free-text reply, following BRIEF.md's tree. "Enough, design now" ends it |
| 4. Scheme | Scheme + Buy | A design model returns the scheme JSON per room. A deterministic validator runs DESIGN.md's ergonomics table, and violations go back to the model (bounded retries). Product search is a separate step (see Catalog) |
| 5. Paint | Paint | Before/after per photo using an image-editing model, following PAINT.md; prompt pack shown when no image provider is configured |
| 6. Present | Present | The same structure as Step 8: before/after slider, Analog/Smart toggle, buyable list with totals, export to HTML/PDF and JSON |

## Architecture (keep it simple)

```
browser (single page, vanilla JS or a light framework)
   │  photos, answers
   ▼
small Node server ── LLM provider (vision + text, structured JSON)
   │             ── image provider adapter (image-to-image "paint")
   │             ── catalog adapter (CSV first, store APIs/feeds later)
   ▼
project folder on disk: the same design/ layout as the skill
(photos/, survey.md|json, brief, scheme, renders/, presentation.html)
```

- **Single-user and local-first for MKI**: no accounts, no database. Files on disk in the skill's `design/` layout, so the agent session and the app share outputs.
- **Validator**: plain code that reads the scheme JSON and DESIGN.md's ergonomics defaults (kept as a data table) and returns `{rule, items, measured, required}` violations. No LLM inside the validator.
- **Secrets**: provider keys in environment variables, never in the browser.

## LLM provider facts (as of 2026-10; verify when building)

If the build uses the Anthropic API (the default for this workspace):
- Use the official SDK (`@anthropic-ai/sdk` for Node), not raw HTTP.
- Model `claude-opus-5-5`. Thinking is adaptive and always on; set `output_config.effort` explicitly (its default is `medium`).
- Photos go as `image` content blocks with a base64 source (`media_type` `image/jpeg`/`image/png`) before the text block. Resize large photos before sending.
- Survey and scheme come back as JSON through `output_config.format` with `type: "json_schema"`. Every object needs `additionalProperties: false`; there are no numeric min/max constraints, so the validator checks ranges.
- Handle `stop_reason: "refusal"` before reading content, and opt into server-side refusal fallbacks (`fallbacks: "default"` with the `server-side-fallback-2026-07-01` beta).
- Forced `tool_choice` is rejected on this model. Use structured outputs or `auto`.
- Re-check these facts against the provider's current documentation (the `claude-api` skill) before writing code; API shapes drift.

Image provider: choose by a small eval rather than by name. It must preserve geometry from a reference image, accept product reference images, cost little per image, and return 16:9. Keep it behind an adapter so it can be swapped. Without a configured provider, the app shows PAINT.md's prompt pack.

## Catalog

- MKI: a hand-curated CSV per store (~50–150 SKUs) with the buyable-list columns from DESIGN.md: category, name, store, price CLP, W × D × H, link, image URL, date seen, and smart/plant attributes.
- Later: official feeds, affiliate programs or store APIs. Scraping store sites only within their terms of use. Every price keeps its date seen.

## Marks

| Mark | Central question | Scope |
|---|---|---|
| MKI | Can photos + interview produce a buyable, ergonomically valid bathroom scheme the owner trusts? | One room type (bathroom), CSV catalog, survey → interview → scheme → validator → presentation; Paint via prompt pack |
| MKII | Do painted after-images keep the geometry well enough to decide on? | Image provider adapter + geometry check UI, all interior room types, Analog/Smart toggle |
| MKIII | Can someone else use it end to end without help? | Exterior zones, catalog refresh, export/share link, error states, cost tracking per project |

## Open decisions for the grilling

1. Who uses it: only the owner (local app) or other people (hosted)? Hosting changes auth, storage and cost.
2. Stack: Node + vanilla JS (simplest), or the workspace's usual framework?
3. Image provider shortlist for the eval, and the budget per image.
4. Catalog source for MKI: which stores and how many SKUs.
5. Where projects live: local folder, or cloud storage.
6. Language of the UI (Spanish first?).
