+++
id = "mn-s36r"
title = "Revert the daily-note snapshot skip (every task line counts)"
kind = "bug"
state = "planned"
created_at = "2026-10-06T00:13:03.156Z"
updated_at = "2026-10-06T02:10:59.213576143Z"
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

### note · external:orchestrator · 2026-10-06T00:49:40.755Z
From orchestrator: option 1. The human reinstalls bridle on the NUC; I'll tell you when it's done, then resume snapshot-revert to finish (docs, check, commit) and merge as usual.

### note · external:orchestrator · 2026-10-06T01:40:30.971Z
From orchestrator: bridle on the NUC is reinstalled (has kill-guard). Go: resume snapshot-revert to finish (docs, check, commit), then merge and tag v2.25.2. New workers are fine again.

### note · external:orchestrator · 2026-10-06T01:50:29.199Z
From orchestrator: I sent snapshot-revert the resume (m-0426); it's running the check now. Your sends fail with 'error: unknown:' likely because the daemon (started 2026-10-01) is older than the new CLI; a daemon restart fixes that, pending the human. If the worker's report doesn't reach you, I'll relay it.

### note · external:orchestrator · 2026-10-06T02:10:45.250Z
From orchestrator, relaying snapshot-revert's report (its send to you likely failed): committed 51b931d7 on its branch, local main merged in, full check green, no snapshot references left in scripts/ or doc/. Ready for your review and merge (v2.25.2).

### note · agent:manager-1 · 2026-10-06T02:10:59.213Z
Review of 51b931d: code, tests and spec are fine, but the brief's doc removals are missing. doc/meta-notes.txt ~line 743 ('Under ## Tasks Due Today and ## Overdue Tasks in a note under...') and scripts/meta_notes/conventions.md lines 17-19 ('Those copies aren't tasks and queries skip them') still describe the skip. Remove both, rerun ./run_tests.sh && uv run pytest test/unit/ && bridle spec check --require-ids, commit, merge main, report counts.
