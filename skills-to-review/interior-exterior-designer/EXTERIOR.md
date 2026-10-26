# Exterior branch

For balconies, terraces, patios, gardens, roofs and facades. Steps 1–9 of the skill stay the same; this file replaces DESIGN.md's rules for exterior zones. Buyable-first, palette, scheme template and works-and-safety from DESIGN.md still apply.

## Extra survey fields

| Field | What to extract |
|---|---|
| Sun | Which way the zone faces; hours of direct sun (ask if unknown); the shade sources |
| Wind and rain | Exposure (sheltered / exposed / high floor); signs of water pooling; where the drain is and the floor slope toward it |
| Railing and edges | Railing height and type, gaps between bars, glass or mesh |
| Surface | Floor material and condition, waterproofing visible or not |
| Services | Outdoor outlet (with cover), tap, lighting points |
| Neighbours and views | Privacy needs, views worth framing, noise |
| Rules | Condominium or municipal limits on closures, colours, awnings, nets, barbecues |

## Rules

**Safety comes before style.**
- Never reduce a railing's height, and never place climbable furniture or planters against it where children or pets live. Check the minimum railing height and bar spacing in local rules (Chile: OGUC); this skill doesn't assume a number.
- Pets: cats need full netting (a "catio") on high floors. Use pet-safe plants only (same check as DESIGN.md › Plants).
- Weight: wet soil and large planters are heavy, and balconies have load limits. Large planters, ponds, hot tubs or heavy pergolas on a balcony or roof need a structural check before going in the scheme.

**Water**
- Keep the drain accessible and the slope working. No decking or rugs that dam water.
- Use planters with saucers or drainage that doesn't stain the facade below.

**Materials**
Choose outdoor-rated products only:
- UV-resistant fabrics and quick-dry cushions.
- Treated wood, aluminium, powder-coated steel or HDPE/rattan-effect furniture.
- Outdoor lamps rated IP44 or higher (IP65 where rain hits them directly).

**Plants**
- Choose by orientation, sun hours, wind, local climate and care time. In windy, high zones, use low, sturdy species and heavy pots, and secure anything that can blow off.
- Irrigation is part of the scheme: by hand, a drip kit, or a self-watering planter.

**Comfort (defaults, verify)**
- Circulation ≥ 800 mm past furniture.
- ≥ 750 mm behind a dining chair to pull it out.
- Side table within reach of every seat.
- Shade for every seat facing the afternoon sun.

**Analog and Smart outdoors**

| Need | Analog | Smart |
|---|---|---|
| Irrigation | Mechanical tap timer | Wi-Fi/Zigbee irrigation controller with a rain or weather skip |
| Lighting | Photocell or switch, solar garden lights | Smart outdoor plug or IP-rated smart lights with schedules |
| Shade | Manual awning or umbrella | Motorised awning with wind sensor |
| Security | Lockable storage box | Outdoor camera or contact sensor (check privacy rules) |

## Built pieces and the building designer

- Pergolas, catio frames, planters, benches and decks that aren't bought ready-made go to `/start-a-proyect` (twin with `/interactive-3d-structure`, quotation, assembly manual).
- Building-level changes are flagged and handed off, never designed here:
  - balcony closures, facade changes, new openings;
  - extensions, roofs over terraces;
  - anything touching structure or waterproofing.

  Write them in the scheme as "needs a professional (architect/engineer) and permits". In Chile that means the municipal works department (DOM) and, in condominiums, the owners' assembly; verify current rules.
- **Building-designer seam:** keep exterior zones as their own sections in `scheme.md` (`## Exterior — <zone>`). A future building/outdoor skill can then pick them up without touching the interior sections.
