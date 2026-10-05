---
id: rg3v
title: Snapshot skip hides real tasks written under Tasks Due Today
kind: bug
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [cru4]
tasks: [mn-hsxc]
---

## The ask


Reported by the notes advisor, 2026-10-05 (notes m-0084): a regression from
[[docs/tickets/resolved/tasks-query-counts-the-daily-note-s-due-today-and-overdue-sn-cru4|cru4]]
(v2.24.1). `scripts/tasks.py` skips every line under a daily note's
`## Tasks Due Today` or `## Overdue Tasks` heading, but the human also writes
real tasks there by hand. In the personal root those are now invisible to
`meta-notes tasks` and `--agenda`: in `plan/daily/26-Q4/2026-10-03 Sat.md`,
"Order school photos" and "Print Zeal's orchestra music" (both due
2026-10-06), "Dr. Westergren, annual visit" (10-19), "mtg: SYM, financial
advisor" (10-20); in Sunday 10-04's note, three undated Walmart tasks.

The rendered snapshot (`find_tasks.py --condensed`) is always a top-level
`- [[link]]` bullet with the copied tasks indented under it:

```
- [[project/Zeal Honors Orchestra 2026]]
  - [ ] Find recordings of the four pieces for Zeal #next 📅 2026-10-06
```

A hand-written task is a top-level `- [ ] ...` line (with its notes and
subtasks indented under it).

## Fix

Under those headings, skip only the lines nested under a top-level
`- [[...]]` bullet (the bullet's whole subtree). Top-level checkbox lines and
their subtrees stay tasks. The "No tasks found matching the criteria." line
needs nothing.
