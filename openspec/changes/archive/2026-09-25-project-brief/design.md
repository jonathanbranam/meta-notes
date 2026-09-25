## Context

`planning-skills` added `scripts/meta_notes/projects.py`, which builds
`meta-notes projects` in steps:

- `list_projects`: projects directly in `project/`, each with its home note,
  fields, and files
- `assign_tasks`: tasks by path and by canonical tag, from one
  `find_tasks.collect_tasks` pass
- `last_review`, `latest_date` (file paths, heading lines, non-`#review`
  task text), and `warnings`

`scripts/meta_notes/project.py` (from `archive-project-status`) has
`project_for`, which accepts `project/` and `archive/project/` paths, and
`home_note` and `read_fields`. `query.task_to_dict` gives the task JSON
shape `meta-notes tasks --json` uses. `cli.py` has subcommand groups
(`task update`, `ceremony status`) and a strict `YYYY-MM-DD` validator
(`_day_value`).

See proposal.md for motivation and `specs/project-brief/spec.md` for
behavior.

## Goals / Non-Goals

**Goals:**
- One code path for a project's tasks, dates, and warnings, so
  `projects` and `project brief` can't disagree.
- The brief's task entries are usable as-is by `meta-notes task update`.

**Non-Goals:**
- Listing `archive/project/` in `meta-notes projects`; only the brief
  accepts archived projects.
- Caching the task pass. One pass per call is fast enough for a notes root
  and matches `projects`.

## Decisions

### Build one `Project` with the code `projects` uses

Split the per-entry body of `list_projects` into
`projects.load_project(rel, root_dir) -> Project | None`, which
`list_projects` calls for each name in `project/` and the brief calls for
its one project. `project brief` then runs the same steps `collect` runs
for a list of one: `assign_tasks`, `last_review`, `latest_date`,
`warnings`. `latest_date` strips the project's parent folder (`project/`
or `archive/project/`) from file paths rather than only `project/`, so a
date in `archive/project/` never counts.

*Alternative:* call `projects.collect` and pick the entry. That rejects
archived projects and computes dates and warnings for every project.

### A new module for the brief

`scripts/meta_notes/brief.py` has `run(root_dir, path, since=None,
today=None) -> (lines, dict)`. It resolves the path with
`project.project_for` (after making an absolute path root-relative),
raises `ValueError` for anything that isn't a project, builds the
`Project`, then splits its tasks:

- `open`: `INCOMPLETE`, not `#later`
- `later`: `INCOMPLETE` and `#later`
- `deadlines`: open `#deadline`; `scheduled_reviews`: open `#review` with
  a due date. Both are views onto `open` and `later`.
- `completed`: `COMPLETED` with `effective_due` on or after `since`
  (default `today - 90 days`); `completed_total` counts every completed
  task, dated or not.

Canceled and rescheduled tasks are dropped. Lists are sorted by file,
then line. Task dicts come from `query.task_to_dict` with `section`
removed. Files get `size` and `modified` from `os.stat`
(`date.fromtimestamp(st_mtime)`, local time).

*Alternative:* put the brief in `projects.py`. The file is already the
list command; a separate module keeps each command's output code apart,
as `ceremony.py` and `conventions.py` do.

### CLI: a `project` group with `brief`

`cli.py` adds `project` as a subcommand group like `task`, with `brief
<path> [--since DAY]`. `--since` uses `_day_value`, so a month or range is
a usage error. `cmd_project_brief` wraps `brief.run` and maps its
`ValueError` to an error `Output`. The group leaves room for later
project commands without another top-level name.

The brief goes under a `project` key in the JSON result. Every `--json`
result already has a top-level `warnings` list of CLI warning messages, so
the project's warning names can't share that name at the top level; nesting
keeps the spec's field names and matches `projects`, whose entries are
under `projects`.

### Text output

A header line (`path  status  tag`, then `latest <date>  review
<date|never>`), a warnings line when there are any, then the sections
from the spec, each a heading followed by indented lines. File lines are
`size  modified  path`. Task lines are `file:line  text`, the same target
`task update` takes. The completed heading is `Completed (N of M since
<date>)`.

## Risks / Trade-offs

- [Archived projects get `review-overdue` and, if `status` isn't set to
  `archived`, `no-next`] → The warnings follow the `project-list` rules
  unchanged, so both commands agree; the review skill ignores warnings on
  archived projects.
- [A large tag produces a long open list] → Only completed tasks are
  windowed; open tasks are the review's working set and stay complete.
- [Modification dates look like activity] → They're reported in the file
  list only, and the spec forbids using them for dates or warnings.
- [Refactoring `list_projects` changes `projects` output] → The existing
  `test_projects.py` tests must pass unchanged.

## Migration Plan

1. Land after `planning-skills`' `projects.py` (already in the tree).
2. MINOR version bump on archive; tag `v<version>`.
3. `project-review-skill` then rewrites the skill against the real output.
