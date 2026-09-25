## Why

Task queries can't tell a live task from a someday item or a plain
checklist, can't filter by tag, and can't say how long a task has sat
untouched. The rituals in `docs/planning-system.md` (morning surface,
project review, weekly review) depend on all of these. Some of this already
exists on the work copy of meta-notes and needs porting back so both copies
share one implementation.

## Dependencies

**Depends on `cli-core`,** which adds `meta-notes tasks` and the
`task-query` capability that this change modifies. Don't start until
`cli-core` is archived.

The work-copy features (`#later`, tag filters, date ranges, trimming) need
the work copy's `find_tasks.py`, or a written description of it, before
their requirements can be written. Task age doesn't, so it can go first.

## What Changes

- **Task model.** A checklist line is a task only when it carries 📆 (with
  or without a date) or `🛫 YYYY-MM-DD`. Plain `- [ ]` items are checklist
  items and are no longer reported. A bare 📆 marks an undated task.
  **BREAKING** for task lists in daily notes, which currently show every
  checkbox. To confirm: does the work copy already behave this way?
- **`#later`.** Excluded from results by default. A flag includes it, listed
  in its own section (text) or flagged per task (JSON).
- **Tag filters.** Filter by one or more `#tag`s, with semantics ported from
  the work copy.
- **Date-range and trimmed output options** ported from the work copy. The
  exact options are recorded in the spec once the work copy has been
  reviewed.
- **Task age.** `meta-notes tasks` reports `last_edited` per task, the author
  date of the task's line from `git blame`. Uncommitted lines report today.
  Blame runs once per file with matching tasks.
- **`--untouched-days N`** returns only open tasks last edited more than N
  days ago.
- The same parsing applies to `scripts/find_tasks.py`, so daily-note
  templates get the new task model and `#later` exclusion. Task age is
  CLI-only, to keep template rendering fast.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities
- `task-query`: task definition (📆 or 🛫 required, bare 📆 undated),
  `#later` handling, tag and date-range filters, trimmed output,
  `last_edited`, and `--untouched-days`.

## Open Questions

- Is the work copy's `find_tasks.py` available to port from?
- Tag matching: exact `#tag` only, or also the aliases and groups in
  `scripts/time_tracking.py`?
- `last_edited` when the notes root isn't a git repo: null, or the file's
  mtime?
- Should `#later` tasks be counted by `--untouched-days`? (Proposed: no,
  unless the `#later` flag is given.)

## Impact

- `scripts/tasks.py`: task definition, bare 📆, `#later` and tag parsing
- `scripts/find_tasks.py`: new filters and sections
- `scripts/meta_notes/query.py`: blame-based `last_edited`,
  `--untouched-days`
- `test/unit/test_tasks.py`, `test_find_tasks.py`, `test_query.py`
- Daily notes rendered from templates: plain checklists and `#later` items
  drop out of task sections
- `skills/project-review/SKILL.md`: can use `meta-notes tasks` for task age
  and tag queries instead of raw `git blame` and grep
