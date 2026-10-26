# LEARNING-PATH-FORMAT.md

`./learning-records/learning-path.md` is the **central roadmap** of the learning journey. It maps the full arc from "knows nothing" to "mission accomplished" in sequential, prerequisite-gated phases. It is the first document to read when resuming a session, and the first to update when progress is made or direction changes.

## Template

```md
# 🛣️ Learning Path: {Topic}

> **Mission**: {One-sentence mission from MISSION.md}
>
> This document is the living roadmap. It is updated dynamically as the learner advances, demonstrates comprehension, and unlocks new domains. Each phase has prerequisites, and each lesson generates learning records that evidence mastery before advancing.

---

## How To Read This Path

| Symbol | Meaning |
|--------|---------|
| ✅ | Phase or lesson completed with evidence |
| 🔵 | Phase or lesson in progress |
| ⬜ | Phase or lesson pending (unlocked) |
| 🔒 | Phase locked (prerequisites not met) |
| 📝 | Learning Record generated as evidence |

---

## Phase 1: {Phase Name} {status symbol}

> **Objective**: {What the learner will be able to do after this phase.}
> **Prerequisites**: None (starting point).

### Lesson NNNN — {Lesson Title} {status symbol}
- **File**: [NNNN-slug.html](../lessons/NNNN-slug.html)
- **Key concepts**: {bulleted list of specific things taught}
- **Interactive tools**: {what the learner interacts with}
- **Assessment**: {how mastery is evaluated}
- 📝 **Learning Records generated**:
  - [LR-NNNN: {title}](./NNNN-slug.md)

---

## Phase N: {Phase Name} 🔒

> **Objective**: {…}
> **Prerequisites**: Phases 1–(N-1) completed.

### Lesson NNNN — {Lesson Title} ⬜
- **File**: `./lessons/NNNN-slug.html` *(to be created)*
- **Planned concepts**: {bulleted list}
- **Planned interactive tools**: {…}
- **Planned assessment**: {…}
- 📝 **Learning Records to generate**:
  - {description of what evidence will be captured}

---

## Learning Record Index (Chronological)

| # | Date | Title | Phase | File |
|---|------|-------|-------|------|
| LR-0001 | YYYY-MM-DD | {title} | Phase N | [NNNN-slug.md](./NNNN-slug.md) |
| LR-0002 | — | *(Pending: {description})* | Phase N | — |

---

## Dynamic Branches (Optional Lessons)

| Optional Lesson | Trigger | Dependency |
|-----------------|---------|------------|
| **OPT-A**: {title} | {what activates it} | Phase N |

---

## Zone of Proximal Development (Current)

> **Current state**: {What the learner knows and can do right now.}
>
> **Recommended next step**: {Which phase/lesson and why.}
>
> **Risk to mitigate**: {What could go wrong if the learner skips ahead.}
```

## Rules

### Structure

- **One learning path per workspace.** It mirrors the single mission. If the mission changes, the path changes with it.
- **Phases are sequential by default.** Each phase unlocks when all previous phases are completed. This prevents the learner from jumping ahead into material they lack foundations for.
- **Lessons within a phase may be parallel.** If two lessons in the same phase are independent, they can be completed in any order.
- **Optional branches live outside the critical path.** They are triggered by learner curiosity or situational needs, not by the phase sequence.

### Status Tracking

- **Update status symbols immediately** when a lesson is completed or a phase transitions. The path should always reflect the true current state.
- **A lesson is only ✅ when a Learning Record evidences comprehension** — not when the learner merely opened or read the lesson. Coverage is not mastery.
- **A phase is only ✅ when all its lessons are ✅.** Partial completion keeps the phase at 🔵.

### Dynamic Modification

- **The learner can redirect the path at any time.** If the user says "I want to learn X instead" or "skip this, I already know it", update the path accordingly. Add a learning record documenting the pivot and the reason.
- **New phases or lessons may be inserted mid-journey.** If a session reveals a gap not covered by existing phases, add a new phase or lesson where it logically fits and re-number if needed.
- **Completed phases are never deleted.** Even if the mission changes, prior phases remain as historical record. Mark them with a note like `(mission pivoted — see LR-NNNN)` if they no longer align.
- **Prior knowledge claims unlock phases.** If the learner says "I already know engines", record it as a learning record with `Evidence: prior knowledge claimed`, mark the relevant phase as ✅, and proceed. If later evidence contradicts the claim, reopen the phase.

### Zone of Proximal Development

- **Update the ZPD section every session.** It is the compass for deciding what to teach next.
- **State the risk explicitly.** What happens if the learner moves forward without this knowledge? This grounds the recommendation.

### Relationship to Other Documents

- The learning path **reads from** `MISSION.md` (to define the destination), `learning-records/` (to track evidence of mastery), and `NOTES.md` (to respect learner preferences).
- The learning path **drives** lesson creation — never create a lesson that isn't on the path (or add it to the path first).
- When a **mission changes**, update both `MISSION.md` and the learning path in the same session.
