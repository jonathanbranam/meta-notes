## 1. Test repository helper

- [x] 1.1 In `test/unit/test_changes.py`, add a fixture that makes a notes root as a git repo in `tmp_path` (`git init`, `user.name`/`user.email` via `-c` or local config, `.meta-notes`) and a helper that commits given file writes, moves, and deletes with fixed `GIT_AUTHOR_DATE` and `GIT_COMMITTER_DATE` (with offset); skip the module if `git` is missing; verify with a smoke test that commits a note on 2026-09-23 and `git log --format=%aI` shows that date

## 2. `changes.py`

- [x] 2.1 Add `scripts/meta_notes/changes.py` with `run(root_dir, date_text=None, today=None) -> (lines, dict)`, a `_git` wrapper running `git --no-optional-locks -C <root>` that raises `ValueError` on a missing binary or non-zero exit, period parsing via `period.parse_period`, and the top-level check against `git rev-parse --show-toplevel`; verify with tests for "Not a git repository", "Notes root below the repository top level", and an invalid `--date`
- [x] 2.2 Parse `git log --reverse --no-merges -M -z --format=%x01%H%x00%aI --raw --numstat --since=<START - 1 day> -- plan project area resource archive` into per-commit change lists (status, paths, added, removed; binary `-` as 0), keeping commits whose `%aI` date is in START..END; verify with tests for "Commit inside the week", "Commit outside the week", "Author timezone decides the day", and a note path containing a space
- [x] 2.3 Fold change sets oldest first into one record per note as the design's table describes (start path, existed at start, deleted, counts, rename-only), derive `kind` by the spec's precedence and `old_path`, keep only `.md` paths, and sort by path; verify with tests for "Non-note files ignored", "Archived note listed", "Several edits to one note", "Archive is rename-only", "Worked on, then archived", "Created this week", and "Deleted this week"
- [x] 2.4 When START ≤ today ≤ END, apply one more change set from `git diff <HEAD or empty tree> -M -z --raw --numstat` plus untracked `.md` notes from `git ls-files --others --exclude-standard -z -- <folders>` (added, counted by lines); verify with tests for "Unstaged edit today", "Untracked note today", "Past period ignores the working tree", "Committed and uncommitted edits combined", "Repository with no commits", and a staged-only edit
- [x] 2.5 Verify read-only behavior: a test that runs `changes` with staged and unstaged edits and checks `.git/index` bytes and mtime, `git status --porcelain`, and `git rev-parse HEAD` are unchanged, and that no `.git/index.lock` remains
- [x] 2.6 Build the result dict (`start`, `end`, `changes` with `path`, `kind`, `old_path`, `added`, `removed`, `rename_only`) and the text lines from the design (kind letter, right-aligned `+N -N`, path, `<- old` for renames, `(rename only)`); verify with tests for the "JSON output" data, the text format of a rename-only and a modified entry, and "Nothing changed" (empty list, no lines)

## 3. CLI

- [x] 3.1 Add the `changes [--date PERIOD]` subcommand and `cmd_changes` in `cli.py`, mapping `ValueError` to `CliError` like `cmd_time`; verify with `test/unit/test_cli.py` tests for "Default period is today", "JSON output" through `main(["changes", "--json", ...])`, and "Not a git repository" with `--json` (`ok` false, one JSON object, nothing on stderr)

## 4. Weekly review skill

- [x] 4.1 Update `skills/weekly-review/SKILL.md`: in "1. Gather", run `meta-notes changes --date MON..FRI --json`, skip `rename_only` entries and notes under `plan/daily/` and `plan/week/`, and continue without it if it fails; in "2. Plan versus actual", ask in one batch about changed notes the other inputs don't account for, with no matching against tasks or time entries; replace the hard rule with "Read git history only through `meta-notes changes`; don't run `git` or read file modification times"; verify by reading the skill against the ceremony-skills delta's scenarios and confirming the other skills' git rule is untouched (`grep -n "git history" skills/*/SKILL.md`)

## 5. Docs

- [x] 5.1 Document `meta-notes changes` in `doc/meta-notes.txt` under a `*meta-notes-cli-changes*` tag (period, what counts as a note, committed and uncommitted changes, entry fields and kinds, rename-only, text format, errors) and add an example to README's Command Line section and its command list sentence; verify `:helptags doc` reports no errors and the tag resolves
- [x] 5.2 In `docs/planning-system.md`, add changed notes to the weekly review's inputs, note in "Task age" that the weekly review's change list is the one use of git history, and add `weekly-review-changes` to the CLI list; verify by reading them against the proposal
- [x] 5.3 Add `changes.py` and `test_changes.py` to the README's project structure tree; verify both appear

## 6. Integration

- [x] 6.1 In a scratch notes root that is a git repo, make commits across a Monday–Friday week and the weekend before it (edits, an add, a delete, an archive with `meta-notes archive`, a move plus edit), leave a staged, an unstaged, and an untracked edit, run `meta-notes changes --date <MON>..<FRI>` with and without `--json` and a past week, and check the entries against the spec; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
