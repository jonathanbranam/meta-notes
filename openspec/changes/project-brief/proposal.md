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
restating them. It reads no git history or `git blame`; `task-age` is
deferred. File modification times are reported in the file list but never
used for the latest date or any other derived date.

The `project-review` skill revision that calls this command is in
`project-review-skill`, which depends on this change.

## What Changes

- Add `meta-notes project brief <path> [--since DATE] [--json]` for a
  note project (`project/foo.md`) or a folder project (`project/foo/`).
- It returns:
  - **Home note and fields:** for a folder, `Home.md`; for a single note,
    the note itself. The fields are the `key: value` items (`status`,
    `tag`, `archived`) in the first list after the home note's title.
    `status` defaults to `active`; a project with no `tag` has no
    associated tag. See "Project model" in `docs/planning-system.md` and
    the `project-fields` spec. No frontmatter is read.
  - **Files:** every file in the project's note or folder, each with its
    size and its modification date (`YYYY-MM-DD`, local time). The
    modification date is informational: moves and link rewrites change
    it, so it doesn't count toward the latest date.
  - **Project tasks:** every task in the project's note or folder, plus
    every task anywhere carrying the project's `tag`, open and completed.
    Completed tasks carry their completion date (✅, or the due date
    without one). Every open task is listed; completed tasks are listed
    when their completion date is within the last 90 days, or on or after
    `--since DATE` when given, and the total count of completed tasks is
    always reported. Checklist lines without `📅` or `🛫` are not tasks and
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
- Only projects, in `project/` or `archive/project/`, are accepted; areas
  are out of scope.

## Capabilities

### New Capabilities
- `project-brief`: the project summary returned by `meta-notes project
  brief`: home-note selection, project fields, files, and project tasks,
  with dates as defined by `project-list`.

### Modified Capabilities

*(none)*

## Impact

- `scripts/meta_notes/`: `project brief` subcommand, reusing the field
  parser in `project.py` (from `archive-project-status`) and the
  per-project tasks, latest date, and last review in `projects.py` (from
  `planning-skills`)
- `test/unit/`: fixture notes root (note and folder projects, tagged tasks
  elsewhere, dated headings, `#later`, `#next`, and `#review` tasks)
- `doc/meta-notes.txt`: command reference
