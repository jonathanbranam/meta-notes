+++
id = "mn-qh2m"
title = "find_tasks --mark-from: copy tasks as [<] 'from' lines so they aren't duplicate tasks; daily templates use it"
kind = "feature"
state = "open"
created_at = "2026-11-09T14:44:26.343Z"
updated_at = "2026-11-09T14:45:06.086312603Z"
created_by = "external:aide"
watchers = ["external:aide"]
ticket = "qh2m"
+++

docs/tickets/open/find-tasks-mark-from-copy-tasks-as-from-lines-so-they-aren-t-qh2m.md

## Thread

### note · agent:manager · 2026-11-09T14:45:03.938Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable.

### note · external:orchestrator · 2026-11-09T14:45:06.086Z
Planning notes (orchestrator). The human's approval is quoted in the ticket; relayed by aide in m-0227. Brief is the ticket body; these add the plan.
Model: Haiku (mechanical, well specified).
Impact list: scripts/tasks.py (STATUS_CHARS; also flows to scripts/meta_notes/conventions.py and cli.py --status choices), scripts/find_tasks.py, after/syntax/markdown.vim, scripts/meta_notes/conventions.md, templates/daily.md, templates/daily-personal.md, test/unit/test_find_tasks.py and the task-status unit tests, test/fixtures/templates/daily-*.md (and test/fixtures/init_templates/daily.md if it mirrors the shipped template), design/specs as needed, CHANGELOG.md, version bump.
Verify: the project's normal check is green; find_tasks.py without --mark-from gives byte-identical output to today; with it, each copied line has [<] and keeps its text, dates and the [[source note]] line in --condensed; a [<] line is absent from --overdue, --due and --agenda; --json reports status from; meta-notes task update --status '<' is accepted; CHANGELOG tells existing roots to add --mark-from to the two template lines by hand.
Deferred: closing the original from a completed copy. Not yet, by the human's decision (see the ticket), because the first version does not need it.
