+++
id = "mn-e5xs"
title = "time-log update rejects an open entry's empty end line"
kind = "bug"
state = "integrated"
created_at = "2026-10-08T01:53:01.699Z"
updated_at = "2026-10-08T02:06:56.105323430Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "agent:manager-1",
]
branch = "bridle/open-end"
commit = "a34ee28"
ticket = "e5xs"
+++


time-log update rejects an open entry's empty end line (ticket docs/tickets/open/time-log-update-rejects-an-open-entry-s-empty-end-line-e5xs.md; it has the repro).

Small bug fix, filed by orchestrator from the meta-notes-ui worker's report on mu-xng2.

Fix: in scripts/meta_notes/time_log.py `_check_new`, treat an empty `end:` value like a missing end line: an open entry, allowed only for the log's last entry (the existing rule for a missing line). Keep the empty line as written. Check `time-log append` and the time report don't choke on the same shape.
Model: Haiku. Size: XS.
Files: scripts/meta_notes/time_log.py, test/unit/test_time_log.py (a test: update keeps an open last entry with an empty end line; an empty end on a non-last entry is still refused).
Verify: ./run_tests.sh green once.
Out of scope: changing the daily template's placeholder lines.

## Thread

### note · agent:open-end · 2026-10-08T02:06:34.796Z
Done on bridle/open-end, commit c18fb8f. Fix: time_log._check_new treats an empty end: as missing (open, last entry only, kept as written). Tests: test/unit/test_time_log.py +2 (open empty end kept on last entry; empty end on non-last refused). Spec: time-log-edit.md (rule sentence + 2 scenarios, ids via bridle spec id), doc/meta-notes.txt one line. Version 2.26.7 -> 2.26.8. Checks: run_tests.sh 183/183 vader (455/455 assertions); uv run pytest test/unit/ 1576 passed, 1 skipped; bridle spec check --require-ids 30 files, 0 errors. time report and time-log append both accept the open empty-end shape (checked by hand). Branch already contains main, no merge needed.

### note · agent:manager-1 · 2026-10-08T02:06:46.118Z
integrated: a34ee28 (branch bridle/open-end)

### note · agent:manager-1 · 2026-10-08T02:06:46.123Z
cleanup: removed nothing

### note · agent:manager-1 · 2026-10-08T02:06:56.105Z
Merged: a34ee28, tagged v2.26.8, task done, worker removed. Worker reported vader 183/183, pytest 1576 passed 1 skipped, spec check 0 errors; I reviewed the diff (one-line fix, 2 tests, spec, doc) and did not rerun the suite. Ticket e5xs left for the orchestrator.
