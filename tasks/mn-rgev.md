+++
id = "mn-rgev"
title = "Calendar: pick up exports from a Calendar Downloads folder and move them into the cache"
kind = "feature"
state = "open"
created_at = "2026-10-08T01:55:45.801Z"
updated_at = "2026-10-08T01:56:05.528360486Z"
created_by = "external:aide"
watchers = ["external:aide"]
+++

original id: rgev

Calendar: pick up exports from a Calendar Downloads folder and move them into the cache. The ticket (docs/tickets/open/calendar-*-rgev.md) is the spec: config keys, move-and-rename with a minute timestamp and no colon, and the three points for you to settle and note.

Approved: the human via aide, 2026-10-08, asked for it to be built ("this should just take care of everything"); their words are on the ticket.

Model: Sonnet. Size: S.
Files likely touched: scripts/meta_notes/calendar.py, scripts/meta_notes/config.py (if keys are validated there), test/unit/test_calendar.py, README.md (Calendar section), doc/meta-notes.txt (meta-notes-cli-calendar, meta-notes-config), the version (minor bump).
Verify: ./run_tests.sh green once; tests for: a matching file is moved and renamed; a non-matching file is left; two in the same minute don't overwrite; a missing folder warns and the calendar still runs from the cache; the moved file is picked as newest.
Out of scope, not yet: watching the folder outside a `calendar` run; copying instead of moving; more than one downloads folder.
