+++
id = "mn-psgg"
title = "Ship a CHANGELOG for users, updated with every version bump"
kind = "feature"
state = "integrated"
created_at = "2026-10-09T03:00:10.188Z"
updated_at = "2026-10-09T03:12:21.694739812Z"
created_by = "external:aide"
watchers = ["external:aide"]
commit = "cd453e9"
summary = "CHANGELOG.md backfilled 2.0.0 to 2.30.0 (user-facing, ASCII); versioning rule now requires an entry with each bump, checked on review; README points to it. Not built: meta-notes --version mentioning it (optional). No version bump."
ticket = "psgg"
+++

docs/tickets/open/ship-a-changelog-for-users-updated-with-every-version-bump-psgg.md

## Thread

### note · external:orchestrator · 2026-10-09T03:00:35.033Z
Readied by orchestrator on the human's approval, via aide (2026-10-08): "It should include new functionality and changes to options and existing functionality." Backfill: "I think backfill but how far? Idk how far back 2.0 is but that sounds fine." Scope and the backfill range (v2.0.0 to now) are on the ticket. Planning note: user-facing summaries of 60 versions need judgement; Sonnet.

### note · agent:changelog · 2026-10-09T03:12:07.891Z
Done on bridle/changelog: CHANGELOG.md (2.0.0 to 2.30.0, user-facing, ASCII), versioning.md rule line, README pointer. Checks: run_tests.sh 184/184, pytest 1623 passed 1 skipped, bridle spec check --require-ids 0 errors. No version bump (docs only). Not done: 'meta-notes --version' mentioning the changelog (ticket said 'could'; skipped).

### note · agent:manager-2 · 2026-10-09T03:12:21.694Z
integrated: cd453e9
