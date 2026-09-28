# Tasks to import once the daemon runs

The first bridle tasks for meta-notes, to create with `bridle task` when the
daemon is up. Delete this file once they're imported.

## task-age (parked)

Was `openspec/changes/task-age/proposal.md` at da4d402 (read it there with
`git show da4d402:openspec/changes/task-age/proposal.md`). Deferred
2026-09-25: planning works from dates already written in the notes, and no
current change needs git history. Revisit only if date-based staleness
proves insufficient.

The gist: planning wants to know how long a task has sat untouched (daily
planning surfaces the 2-3 oldest open tasks; reviews flag stale work), and
today the agent runs `git blame` and grep itself.

- `meta-notes tasks --json` reports `last_edited` per task: the author date
  of the task's line from `git blame` (uncommitted lines report today),
  blaming each file once.
- `--untouched-days N` keeps only selected tasks last edited more than N days
  ago, narrowing whatever the selection modes pick; `#later` tasks stay
  skipped unless `--later` is given.
- CLI only: `scripts/find_tasks.py` doesn't blame, so templates stay fast.
- Modifies the `task-query` spec. Touches `scripts/meta_notes/query.py`,
  `cli.py`, `test/unit/test_query.py`, `test_cli.py`, `doc/meta-notes.txt`
  and `skills/project-review/SKILL.md`.
- Open questions: outside git or for untracked files, is `last_edited` null,
  today or the file's mtime? Show the age in text output or only in JSON?
  Should `--untouched-days` sort oldest first?
