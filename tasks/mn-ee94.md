+++
id = "mn-ee94"
title = "time-block update: race-safe edits of Time Block Plan and Actual cells"
kind = "feature"
state = "integrated"
created_at = "2026-10-01T15:53:39.717Z"
updated_at = "2026-10-01T15:56:49.069028023Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "M"
branch = "bridle/time-block"
commit = "68457c2"
summary = "Added meta-notes time-block update (scripts/meta_notes/time_block.py, shares checkin parsing): finds rows by time, refuses non-empty cells unless --expect matches, --create, --json; spec design/specs/time-block-update.md, doc, README, daily-plan skill and prime.md use it, 23 tests. Version 2.6.0, merged 68457c2, tagged v2.6.0. Ticket move to docs/tickets/resolved/ still pending."
+++

Implement ticket docs/tickets/open/time-block-update-command-gmqp.md (time-block-update-command-gmqp) as written: a 'meta-notes time-block update <file> --time T [--through T] [--plan TEXT] [--actual TEXT] [--expect TEXT] [--create] [--json]' subcommand that finds rows by time, pads cells to the column width, refuses non-empty cells unless --expect matches (error and --json give the current text), and fails clearly (nothing written) on missing Time Block, missing slot without --create, ragged table, or text wider than the column. Share parsing with checkin.py. Also: new spec design/specs/time-block-update.md, doc/ help section, README command list, skills/daily-plan/SKILL.md uses the command to fill Plan, prime.md mentions it, unit tests in test/unit/test_time_block.py, MINOR version bump. Check: ./run_tests.sh && uv run pytest test/unit/ && bridle spec check --require-ids. When merged: move the ticket to docs/tickets/resolved/ with git mv, tag, push main and the tag.

## Thread

### note · agent:manager · 2026-10-01T15:56:47.004Z
integrated: 68457c2 (branch bridle/time-block)

### note · agent:manager · 2026-10-01T15:56:47.009Z
cleanup: removed nothing
