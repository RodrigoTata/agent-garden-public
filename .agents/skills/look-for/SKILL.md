---
name: look-for
description: Hunts for items across classified and marketplace sites (Facebook Marketplace, Mercado Libre, Chileautos, Yapo and others) with a headless browser and returns a verified shortlist. Use when the user wants to find, compare or buy a used car or other second-hand item, or asks to search the marketplaces.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# look-for

Sweep the Chilean marketplaces with a headless browser, verify what comes back, and hand over a shortlist of exactly 3 plus one recommendation. Used cars are the first target; other items follow the same steps with generic fields.

The browser tool is [scripts/browse.mjs](scripts/browse.mjs): one URL in, JSON out (`status`, `text`, `links`, `ldjson`). No install: Node 22+ and Chrome or Edge. Read-only: it never logs in, never submits forms, never messages sellers.

## Walls

A **wall** is a login prompt, captcha, account-verification redirect or an empty page served to a headless browser. `browse.mjs` reports it as `status: login-prompt | blocked | empty`.

- Never climb a wall: no stealth plugins, no captcha solving, no credentials typed on the user's behalf, no retries to wear it down.
- Log it, move to the next site, and offer the **human-assisted run** once at the end: the user logs in by hand in a visible window whose profile persists, then later runs reuse the session. Command and details in [references/sites.md](references/sites.md).
- Facebook Marketplace is walled for anonymous visitors. Reach it only through the user's own session, a few pages at a time, and tell the user once that automated collection may go against Meta's terms.

## Steps

### Step 1 — Brief

Turn the request into a **filter sheet**. Assume Chile, CLP, Región Metropolitana, unless told otherwise. Ask one batched question for the missing essentials only; do not interview.

Cars: make and model, year range, max km, budget ceiling, transmission, fuel, region and how far the user will travel. Other items: item, condition, budget, region.

**Completion criterion:** every filter is either a value or the word `any`, and the user has not been asked a second round of questions.

### Step 2 — Sweep

Read [references/sites.md](references/sites.md), then for every site in its sweep list build the search URL from the filter sheet and run `browse.mjs`. One page at a time, 2 seconds apart, at most 8 page loads per site.

A page that ignores the query (generic highlights instead of the model asked for) is a miss, not a result. Fix the URL once; if it still ignores the query, log it and fall back to the web search tool with `site:<domain> <make> <model>`.

**Completion criterion:** every site in the sweep list has a row in the **sweep log** (`site | URL tried | status | listings found`). A site is never silently skipped.

### Step 3 — Verify

Open each candidate listing page and pull the fields. For vehicles, read [references/used-cars.md](references/used-cars.md) for the fields and the red flags.

Drop listings that break a hard filter. Dedupe the same item posted on several sites (same photos, price, km, year) and keep the cheapest source. Treat a missing field as `?`, never as a guess.

**Completion criterion:** every kept listing has price, year, km (vehicles), location, seller type, URL and source site, with `?` where the page did not say.

### Step 4 — Shortlist

Compare each kept listing with the **comp**: the median price of the verified listings for the same make, model and year band. Deliver:

1. **Filter sheet**: one line.
2. **Options**: exactly 3. Each with Store/site, Price in CLP, Detail (year, km, location, seller), URL, and a Reason (for example "cheapest", "lowest km", "best against the comp").
3. **Recommendation**: one of the 3, with why, balancing price against comp, km, red flags and distance.
4. **Also seen**: a compact table of the runner-ups.
5. **Sweep log**, including every wall hit and the human-assisted run offer when a wall cost coverage.

**Completion criterion:** 3 options with a reason each, one recommendation, and a sweep log that accounts for every site. If fewer than 3 listings survive verification, say so and show what survived, with the filters that cut the rest.
