+++
id = "mn-m9qv"
title = "lists: note format, meta-notes list commands and the agent's list guide"
kind = "feature"
state = "open"
created_at = "2026-11-07T17:09:04.717Z"
updated_at = "2026-11-07T17:09:47.105681349Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "m9qv"
+++

docs/tickets/open/lists-note-format-meta-notes-list-commands-and-the-agent-s-l-m9qv.md

## Thread

### note · agent:manager · 2026-11-07T17:09:47.105Z
Manager: open, not planned, not in bridle queue. I don't plan or queue; please plan and queue it, and I will spawn a Sonnet worker once it is startable. Sizing for the plan: this is a new capability (a note format, a 'meta-notes list' command family with source-task closing, a current-list link, JSON for the UI, and a prime guide section). One worker can take it in one go, but I would split it for review: (A) format spec + list/group/item commands + --json, (B) source tasks (check/uncheck closes/reopens via task update --expect) + current list, (C) prime guide. A then B then C, each its own ticket and minor version. Your call; the plan should name the new files (scripts/meta_notes/list*.py, test/unit/test_list*.py, design/specs/lists.md, doc, README) and the CLI names.
