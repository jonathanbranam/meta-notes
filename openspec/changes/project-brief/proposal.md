## Why

A project review needs a project's full state: its fields, its files, and
its tasks, open and completed, inside the project and anywhere else that
carries its tag. The tasks are the signal of work on the project; there is
no separate "last touched" date. Today the project-review skill gathers
this with half a dozen commands (`git ls-files`, `git log`,
`find_tasks.py`, grep, `git blame`, and a daily-note search). That's slow,
uses a lot of the agent's context, and differs from what the dashboard
will need. One command returns it all, computed the same way for every
caller.

## Dependencies

**Depends on `cli-core`**, **`find-tasks-enhancements`** (for the task
model, `#later`, and tag filters), and **`planning-skills`**, whose
`project-list` capability defines a project's tasks, latest date, last
review, and `no-next` warning for `meta-notes projects`. `project brief`
reuses those definitions and their code for one project instead of
restating them. It reads no git history, `git blame`, or file mtimes;
`task-age` is deferred.

The `project-review` skill revision that calls this command is in
`project-review-skill`, which depends on this change.

## What Changes

- Add `meta-notes project brief <path> [--json]` for a note project
  (`project/foo.md`) or a folder project (`project/foo/`).
- It returns:
  - **Home note and fields:** for a folder, `Home.md`; for a single note,
    the note itself. The fields are the `key: value` items (`status`,
    `tag`, `archived`) in the first list after the home note's title.
    `status` defaults to `active`; a project with no `tag` has no
    associated tag. See "Project model" in `docs/planning-system.md` and
    the `project-fields` spec. No frontmatter is read.
  - **Files:** each with its size
  - **Project tasks:** every task in the project's note or folder, plus
    every task anywhere carrying the project's `tag`, open and completed.
    Completed tasks carry their completion date (✅, or the due date
    without one). Checklist lines without `📅` or `🛫` are not tasks and
    are not reported.
  - **Latest date:** as `project-list` defines it: the latest
    `YYYY-MM-DD` on or before today in the project's file names, its
    markdown headings (for example `## Notes 2026-09-25`), and its
    project tasks other than `#review` tasks, so a review doesn't make a
    stale project look active.
  - **`#later` tasks**, listed separately
  - **Last review:** the latest completion date on a completed `#review`
    task anywhere in the project, or none if never reviewed
  - **`#deadline` tasks and scheduled `#review` tasks**, open, with their
    dates
  - **`has_next`:** whether an open `#next` task exists (a warning if not,
    never an error)
- The caller, not the command, assesses the project from these tasks.
- Only projects are accepted; areas are out of scope.

## Capabilities

### New Capabilities
- `project-brief`: the project summary returned by `meta-notes project
  brief`: home-note selection, project fields, files, and project tasks,
  with dates as defined by `project-list`.

### Modified Capabilities

*(none)*

## Open Questions

- How far back to list completed tasks: all of them, or a recent window
  (for example 90 days) to keep the output small?

## Impact

- `scripts/meta_notes/`: `project brief` subcommand, reusing the field
  parser in `project.py` (from `archive-project-status`) and the
  per-project tasks, latest date, and last review in `projects.py` (from
  `planning-skills`)
- `test/unit/`: fixture notes root (note and folder projects, tagged tasks
  elsewhere, dated headings, `#later`, `#next`, and `#review` tasks)
- `doc/meta-notes.txt`: command reference
