+++
id = "mn-a8aa"
title = "Recurrence 1/5: recurrence rules module"
kind = "feature"
state = "open"
created_at = "2026-09-30T19:59:47.459Z"
updated_at = "2026-09-30T19:59:47.459Z"
size = "M"
+++

Build step 1 of the ticket: scripts/recurrence.py with unit tests. Grammar: every N days|weeks|months|years, optional 'when done', and every weekday (singular 'every day/week/month/year' too, as Obsidian writes them). next_date with month-end clamping. Late completion matches Obsidian: step from the due date even if the result is already overdue; 'when done' steps from the completion date. No CLI yet.

Design: docs/tickets/open/recurrence-and-time-of-day-5vff.md (read the Decisions section first; it overrides the recommendations above it). Follow .bridle/rules (specs, versioning, pytest/vader). Check: ./run_tests.sh && pipenv run pytest test/unit/ pass.
