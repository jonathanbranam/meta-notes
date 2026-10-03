---
id: gjf6
title: "\"no plan\" rows: record unplanned Time Block rows; daily-shutdown fills them"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [bmen, zqqb]
tasks: [mn-bfc6]
closed: 2026-10-03T14:54:18Z
---

# "no plan" rows

## The ask

The human, 2026-10-03 (relayed by the notes advisor, m-0245), approved for
meta-notes: "if the time block passes without a plan, record a short
summary of what happened in actual, and in time blocks, it should say \"no
plan\" to indicate that I didn't make a plan for that block."

For daily-shutdown: "The shutdown skill should be a little bit flexible
here, but in general, if we get all the way to shut down and the plan is
empty, it should confirm with me, but then fill in every plan block with
\"no plan\". That just indicates a failure of planning for that day."

## Changes

- Conventions (`scripts/meta_notes/conventions.md`, Editing the Time
  Block): a past row with an empty Plan gets Plan `no plan` and a short
  Actual summary of what happened.
- `skills/time-block/SKILL.md`: the same, pointing at the conventions.
- `skills/daily-shutdown/SKILL.md`: when Plan cells are still empty at
  shutdown, confirm with the user, then fill each with `no plan`
  (`time-block update --through` sets a range in one call). Flexible, not
  a hard gate.
- Patch release. Mainly for work; home vs work differences come later
  (zyab).
