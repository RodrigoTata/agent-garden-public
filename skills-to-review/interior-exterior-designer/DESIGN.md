# Design rules (interior)

The scheme follows these rules. Exterior zones use [EXTERIOR.md](EXTERIOR.md) instead.

## Buyable first

- Every item is a product a person can buy today: furniture, lamps, curtains and blinds, sanitary ware (sinks, WC, shower sets), faucets, mirrors, storage, textiles, rugs, plants, pots and smart devices.
- Default stores (Chile): Sodimac, Easy, IKEA, Falabella, Paris, Ripley, MercadoLibre. The brief can narrow or widen the list.
- Specs come first, products second. A spec states category, maximum W × D × H in mm, style, material/colour and budget line. `/quotation-for` turns specs into products.
- Prices are retail CLP with VAT, with the date seen. Prices and stock drift, so a scheme older than ~30 days gets re-quoted before buying.
- Custom-built pieces (carpentry, niches, built-ins) only when the brief asks for them, or when no product fits and the owner agrees. Then hand the piece to `/start-a-proyect`.
- Windows and doors: prefer treatments (curtains, blinds, films, handles, seals) over replacing frames. Replacing them is works, not decor.

## Layout

1. Start from the fixed points: plumbing, gas, panel and outlets. Moving them is works with an installer and a cost line.
2. Respect every opening: nothing inside a door swing, and no tall item blocking more than 30 % of a window's width.
3. Place the anchor piece of each room first (bed, sofa, desk, vanity, kitchen run), then circulation, then secondary items.
4. Write every position in mm from a named corner, so the twin and the checks read the same numbers.

## Ergonomics

These starting defaults come from common design guides (Neufert-type references, NKBA kitchen and bath guidelines). Each one is measured in the scheme, not eyeballed. Use the owner's real heights from the brief, and verify against local building rules (Chile: OGUC) where they apply.

| # | Rule | Default |
|---|---|---|
| E1 | Main circulation width | ≥ 900 mm |
| E2 | Kitchen walkway between counters (one cook / two cooks) | ≥ 1000 / ≥ 1200 mm |
| E3 | Kitchen counter height | user elbow height − 100 to 150 mm (typically 850–950) |
| E4 | Kitchen work triangle: sink–hob–fridge, sum of the three legs | 3600–7900 mm |
| E5 | Clear space in front of WC / vanity / shower entry | ≥ 600 (760 recommended) / ≥ 700 / ≥ 700 mm |
| E6 | Washbasin rim height | 800–900 mm |
| E7 | Mirror centre | ≈ eye height of the main user (≈ 0.93 × body height) |
| E8 | Bed: clearance on each accessible side / at the foot | ≥ 600 / ≥ 700 mm |
| E9 | Wardrobe front clearance | hinged: ≥ door leaf width + 300 mm; sliding: ≥ 700 mm |
| E10 | Desk height / seat height / screen top | 720–760 / 420–480 mm / at or just below eye height |
| E11 | Daily-use storage reach | between knee and eye height of the main user |
| E12 | TV viewing distance | ≈ 1.5–2.5 × screen diagonal |
| E13 | Sofa to coffee table | 400–500 mm |
| E14 | Light switch by the door, on the handle side | always (flag missing ones as works) |
| E15 | Tall furniture over 1200 mm | anchored to the wall (child/pet/earthquake safety; Chile is seismic) |

The check table in the scheme lists every rule that applies to the room, with the measured value and pass/fail. A fail is fixed, or accepted by the owner with a reason.

## Light

Three layers in every room: **ambient** (ceiling or indirect), **task** (counter, desk, vanity mirror, reading), and **accent** (shelves, plants, art). Prefer warm white 2700–3000 K in living and bedrooms and neutral 3000–4000 K for kitchen tasks and bathroom mirrors. Write the lamp type and colour temperature into the item spec.

## Palette

One palette across the home, as named in the brief: a main neutral, a wood, a metal and at most one accent colour. Repeat the floor or the wood between rooms for continuity. Check every product's finish against the palette before choosing it.

## Analog and Smart variants

Same layout; only the device layer changes. Each item in the buyable list is tagged `both`, `analog` or `smart`.

| Need | Analog | Smart |
|---|---|---|
| Lighting control | Standard switches, dimmers, plug-in timer for lamps | Smart bulbs or relays, scenes, presence-triggered hall/night light |
| Plugs | Standard outlets, switched power strips | Smart plugs with energy metering |
| Climate | Thermometer/hygrometer, heater with thermostat dial | Temperature/humidity sensors, smart thermostat or IR controller |
| Entrance | Peephole, mechanical lock | Video doorbell, smart lock, door contact sensor |
| Bathroom | Extractor on the light switch | Humidity-triggered extractor, leak sensor under the sink |
| Kitchen | Standard hood | Smoke and leak sensors, smart plug for small appliances |
| Cleaning | Broom and vacuum storage | Robot-vacuum dock space, low-clearance furniture checked (≥ 100 mm under sofas/beds) |
| Windows | Manual curtains/blinds | Motorised blinds or a retrofit curtain motor |

Smart rules:
- One ecosystem (the brief's) or Matter-compatible devices. List the protocol (Wi-Fi, Zigbee, Thread/Matter) and whether a hub is needed.
- Every smart device keeps a working manual control (wall switch, button, key), so nothing breaks when Wi-Fi fails.
- Wired smart devices (switch relays, thermostats) are installer work. Plug-in and battery devices are DIY.
- Show the price difference per room and in total.

## Plants

- Choose by **light** (window or not, which side the window faces), **humidity** (bathrooms are high), **care time** from the brief, and **pets**.
- With cats or dogs, only pet-safe species. Spider plant (*Chlorophytum comosum*) and Boston fern (*Nephrolepis exaltata*) are commonly listed as non-toxic. Pothos, peace lily, snake plant and ZZ plant are commonly listed as toxic. Check the ASPCA list or a vet source for every species before recommending it.
- **Bathroom plant (default proposal):**
  - With a window: a humidity-loving, medium-light species.
  - Without one: a low-light species with a small grow light, or a preserved/artificial plant, stated plainly.
  - Placement: out of the shower spray, not inside any clearance from the ergonomics table.
- The pot and saucer are buyable items too.

## Works and safety

- Damp, mould, cracks, exposed wiring and loose sockets from the survey go first in the scheme, with "fix before decorating".
- Electrical and gas work: certified installer (Chile: SEC-authorised; verify current rules). Plumbing moves: plumber. Load-bearing walls: never touched without a structural engineer and a permit.
- Rented homes: removable solutions first (adhesive hooks, tension rods, plug-in lamps, freestanding storage).

## Template (`design/scheme.md`)

```markdown
# Scheme — <home or project name>
Palette: <name> · Brief confirmed: <date> · Quoted: <date>

## <Room> — <one-line concept>
### Layout (mm from the NW corner)
| Item | Spec / product | Position x, y | Footprint W × D × H | Notes |
|---|---|---|---|---|
| Vanity | 600 × 460 suspended, white, integrated basin | 0, 1200 | 600 × 460 × 450 (rim at 850) | over existing drain |
### Lighting
Ambient: … · Task: … · Accent: …
### Variants
Analog: … · Smart: … · Δ price: CLP …
### Plant
<species> — light/humidity/pet-safe evidence — placement
### Ergonomics check
| Rule | Measured | Required | Result |
|---|---|---|---|
| E5 front of WC | 720 mm | ≥ 600 | pass |
### Works
- <item> — installer — cost line

## Buyable list
| Room | Item | Variant | Store | Product | Price CLP | Real W × D × H | Link | Seen |
|---|---|---|---|---|---|---|---|---|

## Totals
| Room | Analog CLP | Smart CLP |
|---|---|---|
| Total | | |
```
