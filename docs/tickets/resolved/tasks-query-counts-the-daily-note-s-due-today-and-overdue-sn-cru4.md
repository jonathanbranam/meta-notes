---
id: cru4
title: tasks query counts the daily note's Due Today and Overdue snapshot copies as tasks
kind: bug
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: [mn-cru4]
closed: 2026-10-05T11:51:13Z
---

## The ask

Reported by the notes advisor, 2026-10-05 (notes m-0074): `meta-notes tasks
--due --overdue` in the personal notes root lists the copies in daily notes'
`## Tasks Due Today` and `## Overdue Tasks` sections as tasks: 45 lines for
about 5 real ones. And `meta-notes note daily 2026-10-06` copied Monday's
copies into Tuesday's Overdue section, one level deeper
(`plan/daily/26-Q4/2026-10-06 Tue.md`, lines 18-42). The copies are stale
too: they still show tasks since done or re-dated at their source. The human
wants this query reliable; another agent missed due tasks because of it.

## Cause

`templates/daily.md` and `templates/daily-personal.md` fill those two
sections with `find_tasks.py --due/--overdue --condensed` when the note is
made. The task scanner then reads those lines as tasks in the daily note, so
every later query, and every later daily note, picks them up again.

## Fix

Task scanning ignores task lines under the `## Tasks Due Today` and
`## Overdue Tasks` headings of notes under `plan/daily/` (up to the next
`##` heading). Everything that scans tasks goes through it: `meta-notes
tasks`, `find_tasks.py` (the template blocks), `projects`, `brief`.
Tasks written elsewhere in a daily note (Notes, Follow Up, Plan) still count.

Acceptance:
- a unit test: a daily note with a task under each snapshot heading and one
  under `## Notes`; `tasks --due --overdue` returns only the `## Notes` one
  and the source tasks;
- rendering a new daily note from a root whose previous daily note has
  snapshot sections doesn't copy them;
- `run_tests.sh` green; patch version bump per `.bridle/rules/versioning.md`.

Files likely: `scripts/tasks.py` and/or `scripts/find_tasks.py`,
`scripts/meta_notes/query.py`, `test/unit/test_tasks.py` or
`test_find_tasks.py`, `doc/` if it documents what counts as a task,
`scripts/meta_notes/conventions.md` (one line: snapshot sections aren't
tasks; edit the source).

Out of scope: whether the snapshot sections should exist at all, or be
refreshed (not yet: fix the miscount first); the copies already in the
human's notes (the notes advisor cleans those up).

Model: Sonnet.
