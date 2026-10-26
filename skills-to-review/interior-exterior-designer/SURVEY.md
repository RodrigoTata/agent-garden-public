# Survey protocol

How to read current-state photos with vision. Look at each photo in parts: zoom with `/3d-scanner`'s `lupa.mjs` instead of judging the whole frame by eye. The survey records what *is*, never what should be; ideas go to the scheme.

## Per photo

| Field | What to write |
|---|---|
| View | Room, which corner or wall the camera stands at, what it looks toward |
| Anchor | Object of known size in this photo and its plane, or "none" |
| Walls shown | Which walls/faces appear, so every wall of the room is covered by some photo or marked hidden |

## Per room or zone

| Field | What to extract | Why the design needs it |
|---|---|---|
| Type and use | Kitchen, bathroom, bedroom, living, office, entrance, laundry, balcony… and how it is used today | Program |
| Shell dimensions | Wall lengths, ceiling height, niches, columns, beams, steps, with source tags | Layout and fit |
| Openings | Each door (width, hinge side, swing direction) and window (width, height, sill height, opening type, which wall) | Clearances, light, furniture placement |
| Orientation and light | Which way windows face (from the sun direction, shadows or the owner), daylight level (dark / medium / bright), current lamps and their type | Palette, lighting layers, plants |
| Fixed points | Water inlets and drains, WC position, gas, electrical panel, outlets and switches (count and height), radiators, AC, extractor | What can't move cheaply |
| Finishes | Floor, walls, ceiling, countertops, doors: material, colour, condition | Keep, cover or replace |
| Condition issues | Damp stains, mould, cracks, peeling paint, broken tiles, worn joints, rust, water damage, loose sockets | Fix before decorating; may need a professional |
| Existing items | Furniture, appliances, sanitary ware, lamps: approximate size, condition, and keep/sell/discard candidate | The keep list for the brief |
| Style read | Current style in 3 words and what clashes | Starting point for the brief's style questions |
| Hazards | Exposed wiring, missing railing, unsecured tall furniture, slippery floors | Safety items get priority in the scheme |

## Confidence

Measurements use the source tags from `/3d-scanner`: `medido`, `foto ✓`, `foto`, `catálogo`, `supuesto`. Non-measurement fields get a confidence word:

- **seen**: clearly visible in at least one photo.
- **inferred**: deduced from evidence (state the evidence, e.g. "drain under the sink cabinet, inferred from the trap visible through the open door").
- **unknown**: not visible. It goes to the "ask the owner" list.

Typical vision traps to check before writing a value: wide-angle distortion near frame edges, mirrors doubling a room, a door that only looks narrow because it's half-open, dark photos hiding damp, and colours shifted by warm lamps. Report a colour as "under warm light" when the photo is lamp-lit.

## Ask the owner

Close the survey with the list of unknowns that change the design, in this order:
1. Missing anchor measurements.
2. Dimensions a fit depends on (niche width, ceiling height under a beam).
3. Fixed points you couldn't see.
4. Whether condition issues are known or being fixed (who pays, if renting).

Each question names what to measure, from where to where, and your current estimate, as `/3d-scanner` Step 3 does.

## Template (`design/survey.md`)

```markdown
# Survey — <home or project name>
Date: <yyyy-mm-dd> · Photos: <n> in design/photos/

## <Room name> (<type>)
Photos: kitchen-01 (NE corner → SW), kitchen-02 …  · Hidden walls: none | <list>

| Field | Value | Source / confidence |
|---|---|---|
| Shell | 3.40 × 2.60 m, ceiling 2.35 m | medido / foto ±10 % |
| Openings | Window W wall 1.20 × 1.10, sill 0.90 · Door S wall 0.80, hinge left, swings in | foto ✓ |
| Orientation and light | Window faces west; medium daylight; one ceiling bulb | inferred (afternoon shadows) |
| Fixed points | Sink inlet+drain N wall 0.60 from W corner; 3 outlets at 1.10 m | seen |
| Finishes | Floor ceramic beige, good · walls white, stained near window | seen |
| Condition issues | Damp stain under window, ~40 × 30 cm | seen |
| Existing items | Fridge 0.60 × 0.65 × 1.80 (keep?) · table 1.20 × 0.80 (discard?) | foto |
| Style read | dated, beige, cluttered | — |
| Hazards | none seen | — |

## Ask the owner
1. A: window wall length, corner to corner, ≈ 2.60 m?
2. …
```
