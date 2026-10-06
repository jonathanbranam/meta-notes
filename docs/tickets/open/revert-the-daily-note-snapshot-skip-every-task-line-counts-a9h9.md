---
id: a9h9
title: "Revert the daily-note snapshot skip: every task line counts"
kind: bug
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [cru4]
tasks: [mn-s36r]
---

## The ask

## The ask

The human, 2026-10-05 8:12 PM (relayed by the notes advisor, notes m-0086):
"Revert the duplicates fix. I do not like that. That is not okay. That's not
the way this project works. Every place a task is listed, it should always
show up."

Revert the skip added by
[[docs/tickets/resolved/tasks-query-counts-the-daily-note-s-due-today-and-overdue-sn-cru4|cru4]]
(v2.24.1) and narrowed by
[[docs/tickets/resolved/snapshot-skip-hides-real-tasks-written-under-tasks-due-today-rg3v|rg3v]]
(v2.25.1): task scanning lists every task line wherever it is, including
under a daily note's `## Tasks Due Today` and `## Overdue Tasks`.

The duplicates are handled in the notes instead: the notes advisor is
cleaning the old snapshot copies out of the personal root's daily notes, and
its local daily template no longer renders them. The shipped templates are
left for later (the human: "Let's leave the meta notes standard template
for later").

## Decision

Principle, recorded in `design/specs/task-query.md`: a task query lists
every task line in the notes it scans; no section, heading or note is
silently skipped. Duplicates are fixed in the notes or templates, not hidden
by the query.
