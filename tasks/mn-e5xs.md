+++
id = "mn-e5xs"
title = "time-log update rejects an open entry's empty end line"
kind = "bug"
state = "claimed"
created_at = "2026-10-08T01:53:01.699Z"
updated_at = "2026-10-08T02:03:45.710246848Z"
created_by = "external:orchestrator"
watchers = [
    "external:orchestrator",
    "agent:manager-1",
]
+++

original id: e5xs

time-log update rejects an open entry's empty end line (ticket docs/tickets/open/time-log-update-rejects-an-open-entry-s-empty-end-line-e5xs.md; it has the repro).

Small bug fix, filed by orchestrator from the meta-notes-ui worker's report on mu-xng2.

Fix: in scripts/meta_notes/time_log.py `_check_new`, treat an empty `end:` value like a missing end line: an open entry, allowed only for the log's last entry (the existing rule for a missing line). Keep the empty line as written. Check `time-log append` and the time report don't choke on the same shape.
Model: Haiku. Size: XS.
Files: scripts/meta_notes/time_log.py, test/unit/test_time_log.py (a test: update keeps an open last entry with an empty end line; an empty end on a non-last entry is still refused).
Verify: ./run_tests.sh green once.
Out of scope: changing the daily template's placeholder lines.
