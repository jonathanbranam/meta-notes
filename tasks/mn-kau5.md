+++
id = "mn-kau5"
title = "Ceremony skills follow the root mode"
kind = "feature"
state = "integrated"
created_at = "2026-10-04T03:01:00.703Z"
updated_at = "2026-10-04T03:17:17.816499297Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "M"
commit = "f2f8886"
+++

---
id: bup2
title: Ceremony skills follow the root mode
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: [47rb]
see: [zyab]
tasks: []
---

# Ceremony skills follow the root mode

## The problem

The shipped skills assume a work week:

- `daily-shutdown`: "End-of-workday", PR review check (`gh search prs`),
  starred email and Slack saved items; Friday's next day is Monday.
- `daily-plan`: plans the next workday, Monday-Friday; the Monday case.
- `weekly-review`: Friday by 11:00, Monday-Friday only, drafts "a summary
  for the user's manager"; "Weekend work isn't reviewed."
- `weekly-plan`: next Monday-Friday, Friday afternoon, "assume 8:00-17:00".
- `calendar`: Monday-Friday weeks, 1-1 detection, free time in the workday.
- `project-review`: "5-10 minutes between meetings"; next review on the
  next workday. `checkin`: "during the workday".

## Change, by mode

Each skill reads the mode from `meta-notes prime`/`conventions` (47rb) and
branches in its text, rather than shipping a second set of skills:

- **personal**: no PR, Slack or email steps; the next day is tomorrow,
  weekends included; the weekly review covers all seven days, has no
  manager summary, and runs on a day the human picks; the weekly plan
  covers seven days; calendar free time is the personal day (kxxy), no
  1-1s.
- `time-block` keeps `pers:` and `work:` prefixes as written; in personal
  mode `work:` is the exception instead of `pers:`.
- nm28's review step: weekly at work, maybe monthly at home.

## Decided with the human, 2026-10-04

- Personal weekly review and weekly plan happen on Sunday; they cover the
  seven days Monday to Sunday.
- Personal mode drops the daily shutdown: no `- [ ] shutdown complete` in
  a personal daily note, `daily-shutdown` says it's for work roots, and
  `ceremony status` doesn't report it there. `daily-plan` runs on its own.

## Thread

### note · agent:manager · 2026-10-04T03:17:17.816Z
integrated: f2f8886
