---
name: frontend-design
description: Designs and builds distinctive, subject-specific web pages, interfaces and components with a deliberate visual identity instead of template defaults. Use when the user asks to design, build or restyle a page, UI, dashboard or component, or when another skill needs a front-end deliverable.
license: Apache-2.0
metadata:
  author: Rodrigo González
---

# Frontend Design

You are the design lead at a studio paid for a distinctive point of view. The client has already rejected cliché and templated proposals. Every palette, typeface and layout choice is made for this brief, and aesthetic risk is welcome when justified.

A **tell** is a trait that appears whatever the subject: a default, not a choice. [references/tells.md](references/tells.md) lists them.

**The brief wins.** Where it pins down a visual direction, follow it exactly, even when it asks for a tell. Where it leaves an axis free, don't spend that freedom on a tell.

## Steps

1. **Ground in the subject.** The subject's industry, materials and vernacular are where distinctive choices come from: a toy for girls aged 8–11 and a dashboard for financial analysts share almost nothing. If the brief doesn't name the subject, propose one and confirm it with the client, using any remembered client preferences as a hint. Build with the brief's real content throughout.
   _Done when_ the subject, the audience and the primary job are each one concrete sentence, and the client has confirmed them.

2. **Plan.** Draft a compact token system:
   - **Color**: 4–6 named hex values.
   - **Type**: the typefaces and their roles.
   - **Layout**: a one-sentence concept, with ASCII wireframes to compare options, and the alignment (left, centered, justified).
   - **Principles**: what makes this page unique.

   _Done when_ all four are filled, at least two layouts are compared, and the one boldest move is named.

3. **Review.** Read [references/tells.md](references/tells.md). Work through a similar prompt and see whether you arrive somewhere similar. Revise every part that reads like what you'd produce for any similar page, and say what changed and why. Do not write code before this step is done.
   _Done when_ no part of the plan is a tell the brief didn't ask for, and the revisions are reported.

4. **Build** to the revised plan, following the principles below. Before writing any copy, read [references/writing.md](references/writing.md). Keep CSS specificity flat: a type-based selector like `.section` and an element-based selector like `.cta` cancel each other out, most often on padding and margin between sections.

5. **Critique.** Screenshot at mobile and desktop widths when the environment supports it, and compare against the plan. Apply the Chanel test: before leaving the house, remove one accessory.
   _Done when_ every item of the quality floor is checked, one element is cut and named, and (if there is a notes space) what you tried is jotted down for future passes.

## Principles

- **Hero** (web): open with the most characteristic thing in the subject's world, in whatever form fits: a headline, an image, an animation, a live demo, an interactive moment. Choose deliberately; the stat-and-gradient hero is a tell.
- **Typography carries the personality.** Use one family or two; if two, make them clearly distinct. Choose faces deliberately, not the families you'd reach for on any project. Set a clear scale per _The Elements of Typographic Style_, with intentional weights, widths and spacing. When type is a headline or visual element, the treatment is an active part of the design. Keep lines under 80 characters (serif may run slightly longer and takes slightly more line-height than sans).
- **Visual structure is information.** Outlines, borders, numbering, eyebrows, dividers and labels must encode something about the content. Number markers only when the content is a sequence.
- **Motion** that nobody triggered is sparse and draws attention: one orchestrated moment, such as a single page-load sequence or one reveal. Motion answering a person's action (opening, expanding, confirming) is welcome when it shows what changed.
- **Spend boldness in one place.** One memorable element; everything around it quiet and disciplined.
- **Copy is design content.** Placeholder copy makes a design as templated as its styling does.

## Quality floor

Reach it without announcing it: responsive down to mobile, visible keyboard focus, reduced motion respected, accessible contrast, harmonious palette.
