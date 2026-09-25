## Why

The `project-review` skill is a draft that gathers a project's state with
half a dozen commands (`git ls-files`, `git log`, `find_tasks.py`, grep,
`git blame`, a daily-note search), walks through stale tasks one by one,
and triggers on task cleanup. Once `meta-notes project brief` returns a
project's full state in one call and `task-cleanup` owns old tasks, the
skill can be refocused on dead and dormant projects and run monthly.

This revision was split out of `planning-skills` so the other five
skills don't wait on `project-brief`.

## Dependencies

- **`project-brief`**: `meta-notes project brief --json` gives the
  project's fields, files, tasks, last review, and `has_next`.
- **`planning-skills`**: `meta-notes conventions`, which every skill runs
  first; `meta-notes projects`, for picking the project with the oldest
  review; `task-cleanup`, which takes over the stale-task walk; and the
  shared skill requirements in `ceremony-skills`.
- **`archive-project-status`** (archived): the `status` and `archived`
  fields and `meta-notes archive`.

## What Changes

- **`project-review`** (revised): one project per run, monthly, 5–10
  minutes. It starts with `meta-notes conventions`, reads state from
  `meta-notes project brief`, and, when none is named, picks the project
  with the oldest or missing `#review`, skipping `done` projects and
  those with a review scheduled after today. It asks for a disposition
  (continue, pause, done, convert to area, split, merge). Pause and done
  set the `status` field; done offers `meta-notes archive`; converting,
  splitting, and merging use `move`, `note new`, and carried tasks after
  confirmation. It records the review as a completed `#review` task in
  the home note before any `archive` or `move`.
- Its stale-task walk is removed in favor of `task-cleanup`, and its
  description no longer triggers on task cleanup.
- It follows the shared skill shape from `planning-skills`: time budget,
  `meta-notes conventions` first, hard rules, numbered steps with exact CLI
  calls, and a stop section.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities
- `ceremony-skills`: "Shipped skills" lists `project-review`; adds the
  "Project review", "Project review selection", "Project review
  disposition", and "Project review record" requirements.

## Impact

- `skills/project-review/SKILL.md`: rewritten. This supersedes the step 2
  swap listed in `project-brief`'s Impact.
- `docs/planning-system.md`: the project review section matches the skill.
- No CLI or template changes. The shipped skill's behavior changes, so
  archiving bumps the PATCH version.
