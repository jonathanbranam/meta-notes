> **Deferred (2026-09-25).** Planning works from dates already written in
> the notes; no current change needs git history or `git blame`. Revisit
> only if date-based staleness proves insufficient.

## Why

Planning needs to know how long a task has sat untouched. Daily planning
surfaces the 2–3 oldest untouched open tasks, and project and weekly reviews
flag stale work (`docs/planning-system.md`). Today the agent gets this by
running `git blame` and grep itself. Split out of `find-tasks-enhancements`
so the task model and selection modes can ship first.

## Dependencies

- **`find-tasks-enhancements`** defines the task model, the selection modes
  (`--ready`, `--all`, and so on), and `#later`, which this change filters
  and annotates. Start after it is archived.

## What Changes

- **`last_edited`.** `meta-notes tasks --json` reports `last_edited` per
  task: the author date of the task's line from `git blame`. Uncommitted
  lines report today. Blame runs once per file with selected tasks.
- **`--untouched-days N`** keeps only selected tasks last edited more than N
  days ago. It narrows whatever the selection modes pick, so a review of
  every stale task is `--all --untouched-days 30`. Like every mode, it skips
  `#later` tasks unless `--later` is given.
- CLI-only. `scripts/find_tasks.py` doesn't blame, so template rendering
  stays fast.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities
- `task-query`: `last_edited` in JSON results and the `--untouched-days`
  filter.

## Open Questions

1. **Outside git.** When the notes root isn't a git repo, or the file is
   untracked: null, today, or the file's mtime?
2. **Text output.** Show the age in the text report (for example a trailing
   `(untouched 42d)`), or only in JSON?
3. **Sort order.** Should `--untouched-days` sort oldest first rather than by
   file, so "the 2–3 oldest" is just the top of the list?

## Impact

- `scripts/meta_notes/query.py`: blame per file, `last_edited`,
  `--untouched-days`
- `scripts/meta_notes/cli.py`: `--untouched-days` option
- `test/unit/test_query.py`, `test_cli.py`: blame against a temporary git
  repo
- `doc/meta-notes.txt`: `last_edited` and `--untouched-days`
- `skills/project-review/SKILL.md`: can use `meta-notes tasks` for task age
  instead of raw `git blame` and grep
