## Context

The CLI already reads git once: `cli._git` runs `git -C <dir>` for
`--version` and swallows failures. Nothing reads the notes root's history.
Subcommands that take `--date` resolve it with `period.parse_period`, and
report modules follow `time.run(root_dir, date_text, today) -> (lines,
dict)`, with `cli.py` turning `ValueError` into `CliError`. The CLI
`chdir`s to the notes root before running a handler.

The notes root is the repository's top level (proposal.md), and it is a
single user's repo: commits are linear in practice, author and committer
are the same person, and the history is at most a few thousand commits.

See proposal.md for motivation and `specs/change-summary/spec.md` and
`specs/ceremony-skills/spec.md` for behavior.

## Goals / Non-Goals

**Goals:**
- A fixed, small number of git calls per run (at most five: top level,
  HEAD, log, diff, untracked files), however long the period.
- Committed and uncommitted changes go through the same per-note folding,
  so one entry means the same thing whichever side a change came from.

**Non-Goals:**
- Copy detection, rename-similarity tuning, or following a note through
  history before START.
- Merge commits. A single user's notes repo rarely has them; their diffs
  would double-count the branch's commits.
- Working from a notes root below the repository top level (the spec
  makes that an error).

## Decisions

### A `changes` module shaped like `time`

`scripts/meta_notes/changes.py` has `run(root_dir, date_text=None,
today=None) -> (lines, dict)`. It raises `ValueError` for a bad period and
for every git failure (git missing, not a repo, root not the top level),
with the messages the spec names, so `cmd_changes` in `cli.py` is the same
four lines as `cmd_time`. Its own `_git(*args)` runs
`git --no-optional-locks -C <root>`, raising on a non-zero exit; it does
not reuse `cli._git`, which hides failures by design.

The top-level check compares `os.path.realpath` of the root with `git
rev-parse --show-toplevel`. "Not a repository" is that same call failing.

### Committed changes: one `git log` with `--raw --numstat`

```
git log --reverse --no-merges -M -z --format=%x01%H%x00%aI
        --raw --numstat --since=<START - 1 day> -- <PPARA folders>
```

- `--raw` gives each file's status letter (`A`, `M`, `D`, `T`, `R<score>`)
  and paths; `--numstat` gives lines added and removed. Neither alone gives
  both.
- `-z` keeps paths with spaces and unicode intact; `%x01` marks each
  commit's start for splitting.
- `%aI` is the author date in its own offset, so
  `datetime.fromisoformat(...).date()` is the day the spec means. Commits
  outside START..END are dropped in Python.
- `--since` filters on committer date, which is never earlier than author
  date, so it can only prune commits that are too old; the one-day margin
  covers timezone offsets. Without it the whole history is read every run.
- `--reverse` gives oldest first, the order the folding needs.
- The pathspec is the five folder names, so git never diffs `templates/`
  or `.claude/`. A rename from outside the folders into them then shows
  as added, and the reverse as deleted, which is what the entry kinds
  should say anyway. `.md` is filtered in Python.

*Alternative:* `git log --name-status` then `git diff --numstat` per
commit. One process per commit, for no gain.

*Alternative:* `--author-date-order` with `--since` on author date. Git
has no author-date `--since`, so the filter is in Python either way.

### Uncommitted changes: diff against HEAD plus untracked files

When START ≤ today ≤ END:

- `git diff HEAD -M -z --raw --numstat` covers staged and unstaged edits
  to tracked files together, as one change set. With no commits yet,
  diff against the empty tree (`git hash-object -t tree /dev/null`)
  instead of `HEAD`; `git rev-parse --verify -q HEAD` tells which.
- `git ls-files --others --exclude-standard -z -- <PPARA folders>` lists untracked,
  non-ignored files; each `.md` note among them is an add, with `added`
  equal to its line count.

Both are applied after the committed changes, as one last change set.
`--no-optional-locks` keeps `git diff` from refreshing and rewriting the
index, which the spec's read-only requirement rules out.

*Alternative:* `git status --porcelain=v2`. It has status but no line
counts, so the diff would still be needed.

### Folding into one entry per note

A dict maps each note's current path to a record: `start_path`,
`existed_at_start`, `deleted`, `added`, `removed`, `rename_only`. Each
change, oldest first:

| Status | Effect |
|---|---|
| `A` | new record with `existed_at_start` false; if a deleted record already has the path, un-delete it |
| `M`, `T` | add line counts; `rename_only` false |
| `D` | mark deleted; add line counts; `rename_only` false |
| `R` | move the record from old path to new; add line counts; `rename_only` stays true only if both counts are 0 |

A path seen for the first time without `A` gets `existed_at_start` true
and `start_path` equal to that path (the old path, for a rename).
`rename_only` starts true and any non-rename change clears it. The spec's
kind precedence (deleted, added, renamed, modified) is then read off the
record, and `old_path` is `start_path` when it differs from the final path.

Filtering to `.md` happens on the record's paths, so a rename from
`foo.txt` to `foo.md` counts as an add. Binary numstat entries (`-`) count
as 0.

### Output

JSON: `{"ok": true, "start", "end", "changes": [...]}` with the spec's
entry fields. Text: one line per entry,

```
M   +5  -1  area/health.md
R   +0  -0  archive/project/trip.md  <- project/trip.md  (rename only)
A  +12  -0  resource/sourdough.md
```

with the kind as its first letter and the counts right-aligned to the
widest in the list.

### The skill

`skills/weekly-review/SKILL.md` gets a bullet in "1. Gather" for
`meta-notes changes --date MON..FRI --json`, what to skip (`rename_only`,
`plan/daily/`, `plan/week/`), and what to do if it fails. Changed notes
that the other inputs don't already account for go in step 2 as "other
work this week?" questions, in one batch. The hard rule becomes "Read git
history only through `meta-notes changes`; don't run `git` or read file
modification times." The other skills keep their rule unchanged.

## Risks / Trade-offs

- [Git's default rename detection misses a move combined with a large
  edit] → The note appears as deleted plus added; both still show up in
  the review. Accepted per the proposal.
- [A rebase or amend changes committer date but keeps author date, so a
  commit authored before START but committed in the week is read, then
  dropped] → Correct by the spec; only costs parsing.
- [Link rewrites from `move`/`archive` touch many notes, so an archive
  day lists many small `modified` entries] → Visible in the counts; the
  proposal defers a link-only filter until the list proves noisy.
- [`--no-optional-locks` needs git 2.15+ (2017)] → Older git fails the
  command with a clear error, and the review continues without it.
- [Tests depend on a `git` binary] → Tests build repos with fixed
  `GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE` and skip if `git` is missing.
