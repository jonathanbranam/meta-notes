---
id: xq4q
title: "Unapproved-plan rule: 'no plan' goes in Plan, not Actual"
kind: bug
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [qb8e]
tasks: [mn-8f5e]
closed: 2026-10-03T23:04:33Z
---

# Unapproved-plan rule: `no plan` goes in Plan, not Actual

qb8e (v2.14.2) added the rule for an agent's unapproved plan that didn't
happen, but worded it wrong:

- `scripts/meta_notes/conventions.md`: "clear the Plan (leave it empty)
  and set it to `no plan` in Actual". `no plan` belongs in Plan; Actual is
  the short summary.
- `skills/time-block/SKILL.md`: "clear the Plan (leave it empty), set it
  to `no plan`" contradicts itself.

Intended: replace the Plan with `no plan` (not struck) and give Actual a
short summary of what happened, the same as a past row with no plan.
Check `design/specs/time-block-skill.md` says the same. Patch bump.
