# Paint — photoreal "after" images

**Geometry comes from a reference; the AI only paints.** That keeps every image consistent with the survey, the scheme and the buyable list. If an AI invents a room from words, its sizes are fiction and no two views agree.

## Pick the geometry reference per view

| Situation | Reference | Why |
|---|---|---|
| Finishes, decor, lamps, textiles, plants change; furniture stays roughly in place | The survey photo of that view | The real room is the best geometry |
| Layout changes (furniture moves, new kitchen run, walls opened) | A twin view: `/3d-scanner` › `contraste.mjs` puts the twin camera where the photo was taken | The photo shows the old layout, so the twin holds the new one |
| Whole-home overview | Twin axonometric or plan view | No photo shows it |

## Rules

1. **One fresh pass per view.** Always paint from the clean reference, never from an earlier AI image, so errors don't pile up. A rejected image is regenerated from the reference with a corrected prompt.
2. **Lock what must not move.** The prompt names the fixed elements: walls, windows, doors, ceiling height, camera position and lens, plumbing positions.
3. **Products as references.** Attach the chosen products' photos (from the buyable list) when the tool accepts several reference images. Name each product and where it goes.
4. **Decor is illustrative.** Extra props the AI adds (books, vases, fruit, the view outside) are labelled "illustrative" in the presentation unless they're in the buyable list.
5. **Variants and palettes keep the same reference.** Analog vs Smart and palette A vs B are painted from the identical reference, so the slider compares only what changed.
6. **Provenance.** Every image gets a row in `design/renders/render-log.md`.

## Geometry check (before accepting an image)

Compare painted and reference side by side: window and door count and positions, wall corners, ceiling line, fixed plumbing, and the position and proportion of each scheme item. Reject and regenerate if any fixed element moved, appeared or vanished, if a product's proportion is clearly off, or if text/labels are garbled. Record the verdict in the log.

## Prompt pack (when no image tool is available)

One block per view in `design/renders/<view>-prompt.md`, ready to paste into any image-editing tool that accepts a reference image:

```markdown
# <view id> — <room>, <variant>, <palette>
Reference image: design/photos/kitchen-02.jpg   (or design/twin/kitchen-view-02.png)
Product references: <list of product image URLs from the buyable list>

Prompt:
Photorealistic interior photograph of the same room, same camera position and lens.
Keep exactly: <walls, window on the left wall 1.20 m wide, door at right, ceiling height, sink position under the window>.
Change to: <floor: light oak-effect porcelain; walls: warm white; vanity: white suspended 600 mm with integrated basin; mirror: rectangular backlit; lamp: …; plant: … on the shelf right of the mirror>.
Light: <late-afternoon daylight from the west window, warm 3000 K lamps on>.
Style: <palette name>, calm, natural, uncluttered. No text, no people.

Negative: moved windows, extra doors, changed room size, distorted perspective, text.
```

## Render log (`design/renders/render-log.md`)

```markdown
| Image | View | Variant | Palette | Reference | Products referenced | Tool / model | Date | Geometry check |
|---|---|---|---|---|---|---|---|---|
| bano-02-smart.jpg | bano-02 | smart | oak & ivory | photos/bano-02.jpg | vanity, mirror, extractor | <tool name> | 2026-10-18 | pass |
```
