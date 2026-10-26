# Brief — design tree for the grilling

`/grilling` works this tree in rounds: a branch opens only once the decisions it hangs on are settled. Recommend an answer for every question, grounded in the survey. Never ask what the survey or the photos already answer.

## The tree

```
Scope and constraints ──┬─► Occupants ──┬─► Room programs ──► Priorities and phasing
 (rooms, own/rent,      │   (people,    │   (per room: what
  budget, works)        │    pets)      │    it must do)
                        │               │
                        └─► Keep list ──┴─► Style and palette ──► Variants (analog/smart)
                                                               ──► Plants
                                                               ──► Execution (DIY or installer, timeline)
```

## Questions by branch

**1. Scope and constraints** (first round)
- Which rooms/zones are in scope, and is the exterior included?
- Owned or rented? If rented: no drilling? Is the landlord's approval needed? Must changes be removable?
- Apartment in a condominium? Building rules affect balconies, facades and works hours.
- Budget in CLP: total, or per room, with or without works. Is a phased plan acceptable?
- How much works: decor only / furniture and decor / light works (paint, fixtures, lamps) / renovation (tiles, plumbing, electrical, walls).

**2. Occupants**
- Who lives there: number of people, each one's height (cm) and handedness for anyone who cooks or works at a desk, ages, mobility needs.
- Pets: species and habits (cats climb, dogs chew). This drives plant toxicity, fabrics and floor choices.
- Work from home? How many hours, video calls (background), and screens.
- Cooking: little / regular / a lot; one or two cooks at a time.
- Guests and storage pressure: frequent guests? Hobbies with gear (bike, sports, music)?

**3. Keep list**
- From the survey's existing items: keep, move, sell or discard each one. Items kept become fixed inputs to the scheme with their real dimensions.

**4. Room programs** (one block per room)
- What the room must do (e.g. bathroom: shower, storage for 2, a plant; living: seating for N, TV yes/no, reading corner).
- What annoys the owner most about it today.

**5. Style and palette**
- Three words for the feeling they want, and references (photos, Pinterest, the survey's "what clashes").
- Woods and metals they like or refuse; light or dark floors; colour tolerance (neutral / one accent / bold).
- Offer 2–3 named palettes (e.g. "light oak and ivory", "walnut and bronze", "sage and oak") instead of an open question.

**6. Variants**
- Smart ecosystem preference: Google Home, Alexa, Apple Home, Home Assistant, or none. Wi-Fi coverage in every room?
- Things that must stay analog no matter what (e.g. bedroom without screens).

**7. Plants**
- Do they want plants and in which rooms (the bathroom plant is a default proposal)? Do they have time to care for them: low / medium? Is artificial acceptable where light is too low?

**8. Priorities and phasing**
- Which room first? What can wait? Which single change would make the biggest difference to them?

**9. Execution**
- DIY skills (assembly, painting, drilling)? Do they have tools?
- Installers needed (electrician, plumber, gas)? In Chile electrical and gas work goes to installers certified by the SEC (verify current rules).
- Deadline or event driving the date.

## Template (`design/brief.md`)

```markdown
# Brief — <home or project name>
Confirmed by the owner: <yyyy-mm-dd>

## Scope and constraints
- Rooms: kitchen, bathroom, living · Exterior: balcony (yes)
- Tenure: owned · Condominium: yes (works Mon–Fri 9–18)
- Budget: CLP 4,500,000 total, phased OK · Works level: light works
## Occupants
- A: 178 cm, right-handed, works from home 6 h/day · B: 162 cm, cooks a lot · Cat: 1, climbs
## Keep list
- Fridge (0.60 × 0.65 × 1.80): keep · Sofa: sell · …
## Room programs
- Bathroom: shower, storage for 2, one plant, better light
## Style and palette
- "calm, warm, natural" · palette: light oak and ivory · no chrome
## Variants
- Smart: Google Home · bedroom stays analog
## Plants
- Yes, low care, cat-safe only
## Priorities and phasing
- 1) bathroom 2) kitchen 3) living
## Execution
- Assembly and painting DIY; electrician for new ceiling points
## Given by the caller (not asked)
- <decision>: <value> — source
```
