+++
id = "mn-9by4"
title = "Fix test_outlook_refresh_date_only_that_day: fails whenever today is 2026-10-09 (red main)"
kind = "bug"
state = "planned"
created_at = "2026-10-09T03:01:02.515Z"
updated_at = "2026-10-09T03:01:06.186955166Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

Critical: CI on main is red (run 37877148676, commit 34b7f06, ticket-only).

test/unit/test_outlook.py::test_outlook_refresh_date_only_that_day makes `other` for date.today() and `target` for DAY (2026-10-09). In CI, today (UTC) is 2026-10-09, so both are the same file and the "other note unchanged" assert fails. It fails on every run while the date is 2026-10-09 (UTC), and would again whenever DAY is moved to match.

Fix the test, not the code: make `other` a day that can never equal DAY (e.g. DAY + timedelta(days=1), or DAY - 1), keeping the point of the test (only the --date day's note changes). Check the other tests in the file for the same date.today()-vs-DAY pattern and fix those too.
Check: `./run_tests.sh` (or the project's check) green. No version bump if the project's versioning rule skips test-only changes; follow .bridle/rules/versioning.md.
Model: Haiku. Out of scope: anything else in outlook.
