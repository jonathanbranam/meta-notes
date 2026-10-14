+++
id = "mn-h7uc"
title = "Vim: MetaNotesTaskList, a read-only task list buffer like MetaNotesTimeReport"
kind = "feature"
state = "integrated"
created_at = "2026-10-14T20:23:16.453Z"
updated_at = "2026-10-14T20:33:07.021976456Z"
created_by = "external:aide"
watchers = ["external:aide"]
branch = "bridle/tasklist"
commit = "d111d41"
summary = "v2.32.0 (d111d41): :MetaNotesTaskList and <localleader>t show 'meta-notes tasks --agenda' in a reused readonly 'Task List' buffer, grouped by day and file; <CR> on a task opens its file at its line (paths relative to Vim's cwd, the root every plugin command uses). Help, README, CHANGELOG and spec task-query updated; test/task_list.vader. Verified by orchestrator: task_list.vader 4/4, CI green on d111d41."
ticket = "h7uc"
+++

docs/tickets/open/vim-metanotestasklist-a-read-only-task-list-buffer-like-meta-h7uc.md

## Thread

### note · external:aide · 2026-10-14T20:23:29.563Z
From the human, by email via bridle's aide (4:22 PM ET), verbatim: "Feature request for meta-notes - read-only task view. Please send this to the aide at meta-notes for implementation." Filed as mn-h7uc with their spec in full: a MetaNotesTaskList command modeled on MetaNotesTimeReport, a <localleader> mapping, and optionally jump-to-source. 'for implementation' is their go to build it; the size and the mapping key are yours to settle per .bridle/rules (key-mappings.md).

### note · external:orchestrator · 2026-10-14T20:33:06.632Z
integrated: d111d41 (branch bridle/tasklist)

### note · external:orchestrator · 2026-10-14T20:33:06.637Z
cleanup: removed nothing
