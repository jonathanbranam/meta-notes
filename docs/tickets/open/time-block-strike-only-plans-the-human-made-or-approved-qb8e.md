---
id: qb8e
title: "Time Block: strike only plans the human made or approved"
kind: bug
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [gjf6, bmen]
tasks: [mn-d368]
---

# Time Block: strike only plans the human made or approved

The human, 2026-10-03 (relayed by the notes advisor), after an agent
struck through a plan it had filled in itself:

> you made the plan and I didn't approve it and now you struck through it.
> So I don't really need that.

Strike-through (`~text~`) is only for plans the human made or approved. A
plan the agent filled in that the human never approved, and that didn't
happen, is cleared, not struck. The row then has no plan, so the existing
rule applies: Plan `no plan`, Actual a short summary of what happened.

The notes root's `CLAUDE.md` carries this rule for now.

## Change

- `skills/time-block/SKILL.md`, "Rules for the content": the "plan didn't
  happen" rule applies to the human's plans; add the agent's unapproved
  plan case.
- `scripts/meta_notes/conventions.md`, "Editing the Time Block": the same.
- Patch version bump.
