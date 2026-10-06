+++
id = "mn-2dyd"
title = "task update finds the line by --expect (line number optional)"
kind = "feature"
state = "planned"
created_at = "2026-10-06T03:26:57.562Z"
updated_at = "2026-10-06T03:34:13.000002165Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "S"
+++

Ticket: docs/tickets/open/task-update-finds-the-line-by-expect-the-line-number-is-opti-sur9.md (the human chose the design; it's in the ticket).

## Goal
`meta-notes task update <file> --expect '<full first line>' [changes]` without `:LINE`: find the line equal to --expect (same comparison as the existing --expect check). 0 matches: fail. 1: update it. 2+: fail, listing the line numbers, telling the caller to pass FILE:LINE. FILE:LINE unchanged.

## Files
scripts/meta_notes/cli.py (task update's target argument and help), scripts/meta_notes/task_update.py, test/unit/test_task_update.py (and test_cli.py if the argument parsing is tested there), design/specs/task-update.md (new requirement + scenarios, ids via `bridle spec id`), doc/meta-notes.txt (task update section), scripts/meta_notes/conventions.md and skills/*/SKILL.md only where they tell agents to find the line number first (say it's optional now). MINOR bump (2.26.0).

## Check
Tests: no match, one match (with a `$` and other regex characters in the line), two matches (message lists both line numbers), FILE:LINE unchanged, and a file name containing a colon still works the way it does today. Normal project check green.

## Out of scope
Same lookup for task notes / task replace / task show (note in your report whether they could share it). Model: Sonnet. Size: s.

## Thread

### note · agent:update-expect · 2026-10-06T03:34:13.000Z
Done: task update FILE --expect finds the line (v2.26.0), commit 8742dbb. vader 183/183 (455 assertions), pytest 1550 passed 1 skipped, bridle spec check 0 errors. Sharing: task notes/replace/show could reuse task_update.find_line (notes/replace already have --expect; show has none, so it would need one). Note: a target ending in :digits is always FILE:LINE, so a file named like 'x:2' still needs the line given. Docs: doc/meta-notes.txt, conventions.md, one-line daily-plan skill tweak; spec has new requirement + 3 scenarios.
