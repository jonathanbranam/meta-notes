+++
id = "mn-p6ga"
title = "tasks --agenda leaves out started tasks due after the horizon"
kind = "bug"
state = "integrated"
created_at = "2026-10-19T20:22:57.334Z"
updated_at = "2026-10-20T05:30:15.705438607Z"
created_by = "external:aide"
watchers = ["external:aide"]
branch = "bridle/agenda-started"
commit = "04ebfda"
summary = "query.py agenda() now lists a started task that is due after the horizon under Today, by default with no flag (docstring and spec updated). Merge 04ebfda, tag v2.33.1; ticket resolved in c626518."
ticket = "p6ga"
+++

docs/tickets/open/tasks-agenda-leaves-out-started-tasks-due-after-the-horizon-p6ga.md

## Thread

### note · external:orchestrator · 2026-10-19T20:23:33.326Z
Approved by the human (by email via aide, m-0105 / m-0110, 2026-10-19 4:22 PM ET): "Please fix this in the next version." Readied and planned by orchestrator (acting PM). Model: haiku (small, fully specified change in query.py agenda() plus docstring, :help, specs and tests). Out of scope: any new flag. Release as the next meta-notes version.

### note · external:orchestrator · 2026-10-19T20:23:52.404Z
From orchestrator: right, plan failed (ticket settling until 4:32 PM). I will plan and queue it at 4:33 PM; the daemon will nudge you then.

### note · external:orchestrator · 2026-10-20T05:30:13.202Z
integrated: 04ebfda (branch bridle/agenda-started)

### note · external:orchestrator · 2026-10-20T05:30:13.207Z
cleanup: removed nothing
