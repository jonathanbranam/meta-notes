+++
id = "mn-s36r"
title = "Revert the daily-note snapshot skip (every task line counts)"
kind = "bug"
state = "planned"
created_at = "2026-10-06T00:13:03.156Z"
updated_at = "2026-10-06T00:28:38.398938145Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "S"
+++

Ticket: docs/tickets/open/revert-the-daily-note-snapshot-skip-every-task-line-counts-a9h9.md (the human's words and the decision are there).

## Goal
Remove the daily-note snapshot skip (cru4 5205e26, rg3v 9d13cae) so task scanning lists every task line wherever it is. Not a blind `git revert`: keep everything else those commits and later ones did (e.g. `--agenda` from 6eb423e).

## Files
- scripts/tasks.py: remove SNAPSHOT_HEADINGS, `_snapshot_lines` and its use.
- test/unit/test_tasks.py: drop the skip tests; add one that a task under `## Tasks Due Today` / `## Overdue Tasks` of a plan/daily note IS listed.
- design/specs/task-query.md: replace requirement r-a474 and its scenarios with a new requirement (new ids via `bridle spec id`; never reuse old ids) stating the principle: a task query SHALL list every task line in the notes it scans; no section, heading or note is skipped; duplicates are fixed in the notes or templates, not hidden by the query. One scenario: a task under a daily note's `## Tasks Due Today` is listed.
- doc/meta-notes.txt, scripts/meta_notes/conventions.md: remove the text describing the skip.
- PATCH bump to 2.25.2.

## Check
Normal project check green (`./run_tests.sh`, `uv run pytest test/unit/`, `bridle spec check --require-ids`). `grep -rn -i snapshot scripts/ doc/` shows no remaining skip.

## Out of scope
Templates (the shipped daily templates keep their sections for now); editing any notes. Model: Haiku. Size: s.

## Thread

### note · external:orchestrator · 2026-10-06T00:28:38.398Z
From orchestrator: worker snapshot-revert made the edits (tasks.py, spec r-48c2, tests, 2.25.2) but every Bash call it makes is refused: its PreToolUse hook runs `bridle kill-guard`, which the NUC's installed bridle (0.5.0, built 2026-10-05 10:39 UTC) doesn't have. Any worker spawned now hits the same. Please finish this task yourself in the worker's worktree (/srv/shared/work/meta-notes-work/wt/snapshot-revert): check the diff against the brief (also doc/meta-notes.txt and scripts/meta_notes/conventions.md, which the worker didn't mention), run the project check, commit, merge, tag v2.25.2. Don't spawn new workers until I say the CLI is fixed.
