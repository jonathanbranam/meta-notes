---
id: xjaq
title: "Time Block: no plan is struck, ~no plan~"
kind: bug
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [qb8e]
tasks: [mn-xjaq]
---

## The ask

# Time Block: `no plan` is struck, `~no plan~`

The human, 2026-10-06 (to the orchestrator, directly), after installing on
the work computer:

> When I just installed on my work computer, it says "no plan" not struck
> out, but that's incorrect. It should be struck out with a single tilde.

qb8e's wording added "(not struck)" to the `no plan` rule; the human's
words on qb8e were only about not striking the agent's own unapproved
plan. A `no plan` Plan cell is written `~no plan~` (single tildes, never
double) in both cases: the agent's unapproved plan that didn't happen, and
a past row with an empty Plan.

## Change

- `scripts/meta_notes/conventions.md`, "Editing the Time Block": `no plan`
  becomes `~no plan~`; drop "(not struck)".
- `skills/time-block/SKILL.md`, "Rules for the content": the same, both
  bullets.
- `skills/daily-shutdown/SKILL.md`: the fill command becomes
  `--plan '~no plan~'`.
- `scripts/meta_notes/planning.py`: count `~no plan~` as `no_plan`, not
  `crossed_out`; plain `no plan` in older notes still counts as `no_plan`.
  Test in `test/unit/test_planning.py`.
- Any other place that writes or matches `no plan` (grep), e.g. docs.
- `scripts/meta_notes/conventions.md`, "Tasks": the example block gets a
  third line, a task done on its due date, which keeps just its due date
  and no `✅`, e.g. `- [x] Book the dentist 📅 2026-09-22`. The human,
  2026-10-06: "Add another one that shows a completed task that's
  completed on the same date, so that it's clear".
- Patch version bump.

Verify: `meta-notes conventions` prints `~no plan~`; `just check` /
`./run_tests.sh` green; `meta-notes planning` counts both forms as no plan.
