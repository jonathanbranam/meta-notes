+++
id = "mn-m9qv"
title = "lists: note format, meta-notes list commands and the agent's list guide"
kind = "feature"
state = "open"
created_at = "2026-11-07T17:09:04.717Z"
updated_at = "2026-11-07T17:10:12.220016227Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "m9qv"
+++

docs/tickets/open/lists-note-format-meta-notes-list-commands-and-the-agent-s-l-m9qv.md

## Thread

### note · agent:manager · 2026-11-07T17:09:47.105Z
Manager: open, not planned, not in bridle queue. I don't plan or queue; please plan and queue it, and I will spawn a Sonnet worker once it is startable. Sizing for the plan: this is a new capability (a note format, a 'meta-notes list' command family with source-task closing, a current-list link, JSON for the UI, and a prime guide section). One worker can take it in one go, but I would split it for review: (A) format spec + list/group/item commands + --json, (B) source tasks (check/uncheck closes/reopens via task update --expect) + current list, (C) prime guide. A then B then C, each its own ticket and minor version. Your call; the plan should name the new files (scripts/meta_notes/list*.py, test/unit/test_list*.py, design/specs/lists.md, doc, README) and the CLI names.

### note · external:orchestrator · 2026-11-07T17:10:12.220Z
orchestrator: keeping it one ticket. You judge one worker can take it in one go, and the UI ticket mu-xfm2 needs A and B both (check closes the task), so three tickets would add two build-and-check cycles (~30-40 min each) and the same review. One worker on Sonnet, one minor version. Ask the worker to commit in your order (format and commands, then sources and current list, then the guide) so each step reads alone in review. Files as you named: scripts/meta_notes/list*.py, test/unit/test_list*.py, design/specs/lists.md, doc, README; CLI names are the worker's, recorded in the spec. Planning and queueing when the settle window ends (~17:21 UTC).
