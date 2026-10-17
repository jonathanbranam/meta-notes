---
id: mn-edk2
title: Cancelling a recurring task doesn't create its next occurrence
kind: bug
created: 2026-10-17
created_by: external:orchestrator@vesta
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## What happened

Reported by aide on notes (2026-10-17 ~01:46 UTC; vesta-home m-0014). The human was sick and skipped
Friday's evening tasks. Aide cancelled them with `meta-notes task update <file>:<line> --status -`.
Each was a recurring task (`🔁 every day`). The cancel set `[-]` but made no next occurrence, unlike
`--status x`, so the series stopped. Aide re-added Saturday's four tasks by hand in
`area/home/Home.md` (notes repo).

## Cause

`scripts/meta_notes/task_update.py` (~line 539): the next occurrence is spawned only when the
new status is in `DONE_CHARS` and the old one wasn't. `-` (cancelled) isn't in `DONE_CHARS`, so a
cancel never rolls the recurrence. There is no skip option either.

## The ask

Cancelling a recurring task should be usable as "skip this one": the series carries on.
Either:

- cancelling with `-` rolls the recurrence like `x` does, with `--no-recur` to end the series;
- or a separate skip (for example `--skip`), with `-` left as it is.

Recommendation: the first option: a skipped day shouldn't end a daily series, and it needs no new
flag. Check what Obsidian Tasks does on cancel first, since the files follow its format.
Settle the choice before planning.

## Check

A test: `task update --status -` on a `🔁 every day` task with a due date adds the next day's
line; with `--no-recur` it doesn't.

Model: Haiku (small change and a test).

## Approval

The human, via aide (notes), 2026-10-17 ~02:00 UTC (vesta-home m-0015): "Agree for edk2 you mean
cancelling right? [-]". Aide confirmed: cancelling with `[-]` on a recurring task rolls the series
like `[x]`, with `--no-recur` to end it. Build the first option above.
