## Why

A project review needs a project's full state: what's in it, when it last
really changed, its open tasks inside and elsewhere, and when time was last
logged against it. Today the project-review skill gathers this with half a
dozen commands (`git ls-files`, `git log`, `find_tasks.py`, grep,
`git blame`, and a daily-note search). That's slow, uses a lot of the
agent's context, and differs from what the dashboard will need. One command
returns it all, computed the same way for every caller.

## Dependencies

**Depends on `cli-core`**, **`find-tasks-enhancements`** (for the task
model, `#later`, and tag filters), and **`task-age`** (for `last_edited`).

## What Changes

- Add `meta-notes project brief <path> [--json]` for a note project
  (`project/foo.md`) or a folder project (`project/foo/`).
- It returns:
  - **Index note and frontmatter:** for a folder, `index.md`, else the note
    named after the folder; for a single note, the note itself. Frontmatter
    is simple `key: value` pairs, with inline `# comments` stripped. It is
    read-only.
  - **Files:** each with size and last change date, the most recent commit
    touching it (following renames), or today if it has uncommitted
    changes.
  - **Open tasks inside the project**, each with `last_edited`
  - **Open tasks elsewhere** that link to `[[<project path>` or carry the
    frontmatter `tag:`
  - **`#later` tasks**, listed separately
  - **`has_next`:** whether an open `#next` task exists (a warning if not,
    never an error)
  - **Last ✅ date** on a task inside the project
  - **Last logged:** the most recent daily note whose time log (Log section
    or Actual column) mentions the tag or a link to the project
  - **Last touched:** the latest of the last change, last ✅, and last
    logged dates, as defined in `docs/planning-system.md`
- The CLI makes no git writes, so moves and link rewrites committed with the
  day's edits count as changes. A filter for link-only and header-only diffs
  is a possible follow-up.

## Capabilities

### New Capabilities
- `project-brief`: the project summary returned by `meta-notes project
  brief`, including index-note selection, derived dates, and related tasks.

### Modified Capabilities

*(none)*

## Open Questions

- Canonical note for folder projects: `index.md`, falling back to the
  folder-named note (the skill's rule), or `index.md` only? This is still
  open in the planning doc.
- Tag matching against time logs: apply the aliases and groups in
  `scripts/time_tracking.py`?
- Should `project brief` also accept areas (`area/<name>`)?
- Interaction with `time-log-hhmm-format`, which changes time-log parsing
  that "last logged" reuses

## Impact

- `scripts/meta_notes/`: `project brief` subcommand, frontmatter reader,
  and git history helpers (read-only `git log` and `git status`)
- `scripts/time_tracking.py`: reused for Log and Actual parsing
- `test/unit/`: fixture notes repo with git history (renames, uncommitted
  edits, time logs, `#later` and `#next` tasks)
- `skills/project-review/SKILL.md`: step 2 becomes one
  `meta-notes project brief --json` call
- `doc/meta-notes.txt`: command reference
