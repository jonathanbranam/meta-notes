+++
id = "mn-ee94"
title = "time-block update: race-safe edits of Time Block Plan and Actual cells"
kind = "feature"
state = "planned"
created_at = "2026-10-01T15:53:39.717Z"
updated_at = "2026-10-01T15:53:42.508451467Z"
size = "M"
+++

Implement ticket docs/tickets/open/time-block-update-command-gmqp.md (time-block-update-command-gmqp) as written: a 'meta-notes time-block update <file> --time T [--through T] [--plan TEXT] [--actual TEXT] [--expect TEXT] [--create] [--json]' subcommand that finds rows by time, pads cells to the column width, refuses non-empty cells unless --expect matches (error and --json give the current text), and fails clearly (nothing written) on missing Time Block, missing slot without --create, ragged table, or text wider than the column. Share parsing with checkin.py. Also: new spec design/specs/time-block-update.md, doc/ help section, README command list, skills/daily-plan/SKILL.md uses the command to fill Plan, prime.md mentions it, unit tests in test/unit/test_time_block.py, MINOR version bump. Check: ./run_tests.sh && uv run pytest test/unit/ && bridle spec check --require-ids. When merged: move the ticket to docs/tickets/resolved/ with git mv, tag, push main and the tag.
