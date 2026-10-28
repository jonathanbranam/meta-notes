---
id: mn-8se5
title: "Conventions: Actual records only deviations; leave it blank when the plan happened"
kind: docs
created: 2026-10-28
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## Ask

From the human (2026-10-28), via aide (notes), verbatim:

> "As long as actual matches planned, then we don't fill out actual. Because it says 'work' and just
> says 'work' for the planned, and I worked, then we don't need to fill out the actual here. If
> something happens, if I planned it to work and then I go home in the middle of the day for some
> reason, then we would actually fill out the actual, because you only fill out actual if it's
> different. There's no reason to copy the plan into actual, and we have a time log. The time log
> covers in minute detail what happened. The main purpose of actual is to record deviations from
> the plan, so that otherwise they're not visible anywhere else. If that is not clear in the
> meta-notes convention, then please ask the aide to get that clarified."

## Gap

The time-block skill already says "The plan happened: leave Actual blank". But
`scripts/meta_notes/conventions.md`, section `## Editing the Time Block` (what
`meta-notes conventions` prints), only covers rows that "didn't go as planned" and never says to
leave Actual blank when the plan happened. The notes aide copied the Plan into Actual on
2026-10-28 because of this.

## Change

In `## Editing the Time Block` of `scripts/meta_notes/conventions.md`, state outright:

- Actual records only deviations from the Plan and extras not in it.
- A row that went as planned keeps Actual blank.
- Never copy the Plan into Actual.
- The Time Log holds the minute-by-minute detail; Actual is where deviations stay visible.

Keep the existing struck-plan rules as they are. ASCII only. If a test pins the conventions text,
update it; bump the patch version and CHANGELOG per the project's usual practice.

## Verify

`meta-notes conventions` shows the new text; the project's checks pass.

Model: haiku (short docs edit). Out of scope: changing the time-block skill or CLI behaviour.
