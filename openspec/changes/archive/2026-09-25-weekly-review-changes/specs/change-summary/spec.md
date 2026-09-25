## Purpose

Specifies `meta-notes changes`, which lists the notes changed in a period from the notes root's git history and working tree, so a review can find work that never became a task or a time-log entry.

## ADDED Requirements

### Requirement: Changes command
`meta-notes changes [--date PERIOD] [--json]` SHALL list the notes changed in PERIOD, where PERIOD uses the `date-period` syntax and defaults to today. A note is a `.md` file under `plan/`, `project/`, `area/`, `resource/`, or `archive/`, at any depth. Files outside those folders, and files that aren't `.md`, SHALL NOT be listed. Notes under `archive/` SHALL be listed like any other note.

#### Scenario: Default period is today
- **WHEN** today is 2026-09-25 and `meta-notes changes` is run with no `--date`
- **THEN** the list SHALL cover 2026-09-25 only

#### Scenario: Non-note files ignored
- **WHEN** a commit in PERIOD changes `project/kitchen/plan.pdf`, `templates/daily.md`, and `project/kitchen/Home.md`
- **THEN** only `project/kitchen/Home.md` SHALL be listed

#### Scenario: Archived note listed
- **WHEN** a commit in PERIOD edits `archive/project/trip.md`
- **THEN** `archive/project/trip.md` SHALL be listed

### Requirement: Committed changes in the period
A commit SHALL be in PERIOD when its author date, taken in the timezone recorded with that date, falls on or between START and END. Commits outside PERIOD SHALL NOT contribute to the list.

#### Scenario: Commit inside the week
- **WHEN** a commit authored 2026-09-23 edits `area/health.md` and the command is run with `--date 2026-09-21..2026-09-25`
- **THEN** `area/health.md` SHALL be listed

#### Scenario: Commit outside the week
- **WHEN** the only commit editing `area/health.md` was authored 2026-09-19 and the command is run with `--date 2026-09-21..2026-09-25`
- **THEN** `area/health.md` SHALL NOT be listed

#### Scenario: Author timezone decides the day
- **WHEN** a commit's author date is `2026-09-25T23:30:00-07:00`
- **THEN** it SHALL be in `--date 2026-09-25` and SHALL NOT be in `--date 2026-09-26`

### Requirement: Uncommitted changes
When PERIOD includes today, the list SHALL also include notes with uncommitted changes: staged, unstaged, and untracked (but not ignored) files. When PERIOD does not include today, uncommitted changes SHALL NOT be listed.

#### Scenario: Unstaged edit today
- **WHEN** today is 2026-09-25 and `resource/vim.md` has an unstaged edit
- **THEN** `meta-notes changes --date 2026-09-21..2026-09-25` SHALL list `resource/vim.md`

#### Scenario: Untracked note today
- **WHEN** today is 2026-09-25 and `project/new-idea.md` is untracked
- **THEN** `meta-notes changes` SHALL list `project/new-idea.md` as added

#### Scenario: Past period ignores the working tree
- **WHEN** today is 2026-09-25 and `resource/vim.md` has an unstaged edit
- **THEN** `meta-notes changes --date 2026-09-14..2026-09-18` SHALL NOT list it because of that edit

### Requirement: One entry per note
The list SHALL have one entry per note, combining all of its committed and uncommitted changes in PERIOD, sorted by path. Each entry SHALL have:
- `path`: the note's path at the end of PERIOD, or for a deleted note its last path
- `kind`: `deleted` if the note no longer exists at the end of PERIOD; otherwise `added` if it did not exist at the start of PERIOD; otherwise `renamed` if its path changed; otherwise `modified`
- `old_path`: the note's path at the start of PERIOD for `renamed`, and null otherwise
- `added` and `removed`: the lines added and removed across all its changes in PERIOD
- `rename_only`: true when every change to the note in PERIOD was a rename with no lines added or removed

Renames SHALL be detected as git detects them by default; a rename git does not detect SHALL appear as a deleted note and an added note.

#### Scenario: Several edits to one note
- **WHEN** three commits in PERIOD edit `project/kitchen/Home.md`, adding 4, 2, and 1 lines and removing 1
- **THEN** there SHALL be one entry for it with kind `modified`, `added` 7, and `removed` 1

#### Scenario: Committed and uncommitted edits combined
- **WHEN** today is in PERIOD, a commit in PERIOD adds 3 lines to `area/health.md`, and an unstaged edit adds 2 more
- **THEN** there SHALL be one entry for `area/health.md` with `added` 5

#### Scenario: Archive is rename-only
- **WHEN** a commit in PERIOD moves `project/trip.md` to `archive/project/trip.md` with no content change
- **THEN** the entry SHALL have path `archive/project/trip.md`, kind `renamed`, old path `project/trip.md`, and `rename_only` true

#### Scenario: Worked on, then archived
- **WHEN** one commit in PERIOD edits `project/trip.md` and a later one moves it to `archive/project/trip.md`
- **THEN** the entry SHALL have path `archive/project/trip.md`, kind `renamed`, old path `project/trip.md`, and `rename_only` false

#### Scenario: Created this week
- **WHEN** a commit in PERIOD adds `resource/sourdough.md` and a later one edits it
- **THEN** its one entry SHALL have kind `added`

#### Scenario: Deleted this week
- **WHEN** a commit in PERIOD deletes `project/old.md`
- **THEN** the entry SHALL have path `project/old.md` and kind `deleted`

### Requirement: Changes output
With `--json`, the command SHALL write one object with `ok` true, `start` and `end` as `YYYY-MM-DD`, and `changes`, the list of entries. Without `--json`, it SHALL print one line per entry with its kind, lines added and removed, and path, followed by the old path for a rename and a marker for rename-only; a period with no changes SHALL print nothing and succeed.

#### Scenario: JSON output
- **WHEN** `meta-notes changes --date 2026-09-21..2026-09-25 --json` is run and only `area/health.md` was modified, with 5 lines added and 1 removed
- **THEN** the output SHALL be `ok` true, `start` `2026-09-21`, `end` `2026-09-25`, and one change with path `area/health.md`, kind `modified`, `old_path` null, `added` 5, `removed` 1, `rename_only` false

#### Scenario: Nothing changed
- **WHEN** no note changed in PERIOD
- **THEN** the command SHALL succeed; with `--json`, `changes` SHALL be empty, and without it nothing SHALL be printed

### Requirement: Changes are read-only and need git
The command SHALL NOT write any file, change the git index, or create commits, refs, or lock files. It SHALL fail with an error when `git` is not available, when the notes root is not the top level of a git working tree, or when PERIOD is invalid.

#### Scenario: Index untouched
- **WHEN** `meta-notes changes` runs in a notes root with staged and unstaged edits
- **THEN** the index, the working tree, and the commit history SHALL be unchanged

#### Scenario: Not a git repository
- **WHEN** the notes root is not in a git working tree
- **THEN** the command SHALL exit non-zero with an error saying the notes root is not a git repository

#### Scenario: Notes root below the repository top level
- **WHEN** the notes root is a subdirectory of a git working tree
- **THEN** the command SHALL exit non-zero with an error saying the notes root must be the top level of its git repository

#### Scenario: Repository with no commits
- **WHEN** the notes root is a new git repository with no commits and an untracked `project/foo.md`
- **THEN** `meta-notes changes` SHALL succeed and list `project/foo.md` as added
