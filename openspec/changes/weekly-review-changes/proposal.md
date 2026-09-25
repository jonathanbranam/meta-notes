## Why

The weekly review drafts from completed tasks, the time report, and daily
notes. Work that never becomes a task is missed: a design doc written, a
meeting's notes, a resource page cleaned up. The notes root is a git repo
committed daily, so the files I changed in a week are already recorded.
Listing them gives the review a second source for "what I did this week".

## Dependencies

- **`planning-skills`**: the `weekly-review` skill this change augments.
- **`date-period`** (archived): the shared `--date` syntax.

## What Changes

- Add `meta-notes changes [--date PERIOD] [--json]`, which lists the notes
  (`.md` files under the PPARA folders) changed in PERIOD, defaulting to
  today:
  - committed changes whose author date falls in PERIOD
  - uncommitted changes (staged, unstaged, untracked) when PERIOD includes
    today
  - one entry per note under its current path, with the change kind
    (added, modified, deleted, renamed), lines added and removed, and its
    old path for a rename
  - rename-only changes (a move with no content change, such as an
    archive) marked so they can be ignored
- Read-only: no git writes, no index changes. Outside a git repo the
  command fails with a clear error.
- `weekly-review` runs `meta-notes changes --date <Monday>..<Friday>` for
  the workweek it reviews (weekend work isn't covered) and uses it
  to augment the summary. It skips rename-only entries and daily and weekly
  plan notes (already read directly). It asks about changed files that no
  completed task or time-log entry explains. If the command fails, the
  review continues without it.

## Capabilities

### New Capabilities
- `change-summary`: notes changed in a period, from git history and the
  working tree

### Modified Capabilities
- `ceremony-skills`: `weekly-review` gains the change list as an input

## Non-Goals

- Per-task last-edited dates or `git blame`. `task-age` stays deferred.
- Filtering out edits that only rewrite links or headers. Rename-only is
  the one filter; a link-only filter can come later if the list is noisy.

## Impact

- `scripts/meta_notes/`: new `changes` module and subcommand
- `skills/weekly-review/SKILL.md`: a changes step
- `test/unit/`: tests against a temporary git repo (commits across days,
  renames, uncommitted and untracked edits)
- `doc/meta-notes.txt`, `README.md`: command reference and example
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
