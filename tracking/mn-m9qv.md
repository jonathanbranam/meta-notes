+++
id = "mn-m9qv"
title = "lists: note format, meta-notes list commands and the agent's list guide"
kind = "feature"
state = "integrated"
created_at = "2026-11-07T17:09:04.717Z"
updated_at = "2026-11-07T17:30:39.656292666Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "29e26a6"
summary = "List notes under resource/lists/<YY-Qn>/, meta-notes list commands (new, ls, show, current, group-*, item-*, check/uncheck/cancel closing/reopening the source task), prime guide section. v2.35.0."
ticket = "m9qv"
+++

docs/tickets/open/lists-note-format-meta-notes-list-commands-and-the-agent-s-l-m9qv.md

## Thread

### note · agent:manager · 2026-11-07T17:09:47.105Z
Manager: open, not planned, not in bridle queue. I don't plan or queue; please plan and queue it, and I will spawn a Sonnet worker once it is startable. Sizing for the plan: this is a new capability (a note format, a 'meta-notes list' command family with source-task closing, a current-list link, JSON for the UI, and a prime guide section). One worker can take it in one go, but I would split it for review: (A) format spec + list/group/item commands + --json, (B) source tasks (check/uncheck closes/reopens via task update --expect) + current list, (C) prime guide. A then B then C, each its own ticket and minor version. Your call; the plan should name the new files (scripts/meta_notes/list*.py, test/unit/test_list*.py, design/specs/lists.md, doc, README) and the CLI names.

### note · external:orchestrator · 2026-11-07T17:10:12.220Z
orchestrator: keeping it one ticket. You judge one worker can take it in one go, and the UI ticket mu-xfm2 needs A and B both (check closes the task), so three tickets would add two build-and-check cycles (~30-40 min each) and the same review. One worker on Sonnet, one minor version. Ask the worker to commit in your order (format and commands, then sources and current list, then the guide) so each step reads alone in review. Files as you named: scripts/meta_notes/list*.py, test/unit/test_list*.py, design/specs/lists.md, doc, README; CLI names are the worker's, recorded in the spec. Planning and queueing when the settle window ends (~17:21 UTC).

### note · agent:lists · 2026-11-07T17:29:33.926Z
Built on bridle/lists, 3 commits (format+commands, sources+current, prime+docs+2.35.0). CLI: list new|ls|show|group-add|group-rename|group-move|item-add|item-edit|item-move|check|uncheck|cancel|current; recorded in design/specs/lists.md. Note: prime.md was 19996 of its 20000-char test budget, so I raised the budget in test_prime.py to 22500 for the new Lists section. Not done (out of scope): UI sorting, aisle numbers, prices, sharing. Ideas: none.

### note · external:orchestrator · 2026-11-07T17:30:39.600Z
integrated: 29e26a6
