# Sweep list

Sites for Chile, in sweep order. Statuses come from a first test on 2026-10-25 with a fresh headless profile; sites change, so a row is a starting point and the sweep log is the truth. When you verify a URL pattern that works, update its row.

| Site | Domain | Search URL | Last status (headless, anonymous) |
|------|--------|------------|-----------------------------------|
| Mercado Libre | mercadolibre.cl | `https://listado.mercadolibre.cl/autos-usados/<make>-<model>` | Redirected to `account-verification`: wall |
| Chileautos | chileautos.cl | `https://www.chileautos.cl/vehiculos/autos-veh%C3%ADculo/<make>/<model>/` | Empty page (0 chars) even after 8 s: wall |
| Facebook Marketplace | facebook.com | `https://www.facebook.com/marketplace/santiago/search?query=<make>%20<model>` | Shell loads with a login prompt, listings hidden: wall |
| Yapo | yapo.cl | `https://www.yapo.cl/autos?q=<make>%20<model>` | Loads and lists cars, but `q` was ignored: generic highlights. Look for a make or model path before trusting it. |
| Kavak | cl.kavak.com | not tested | Add after a first run |

Listing links: Yapo `…/autos-usados/<slug>/<id>`; Facebook `…/marketplace/item/<id>/`. The link text on result pages already carries price, make, model, location, year and km, so read the result page before opening each listing.

## Web search fallback

When a site is walled or ignores the query, use the agent's web search with `site:<domain> <make> <model> <year>`. Snippets carry price and year often enough to seed Step 3, but every snippet must be confirmed by opening the listing, which is subject to the same walls.

## Human-assisted run

The user logs in once, by hand, in a visible window; the profile keeps the session.

```
node scripts/browse.mjs "<search URL>" --headed --profile "%USERPROFILE%\.look-for\profile" --hold 90
```

- `--hold 90` keeps the window open 90 seconds for the user to log in or solve a captcha, then the script reads the page.
- Later runs: same command without `--headed`. A site that still serves an empty page to headless needs `--headed` every time.
- The profile holds the user's session cookies. Keep it outside every repository and never copy or print it. Only one browser can use a profile at a time.
- Read-only still applies: no messages, no offers, no saved searches, no "contact seller".
