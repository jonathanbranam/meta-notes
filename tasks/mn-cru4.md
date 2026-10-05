+++
id = "mn-cru4"
title = "tasks query counts the daily note's Due Today and Overdue snapshot copies as tasks"
kind = "bug"
state = "integrated"
created_at = "2026-10-05T11:37:25.857Z"
updated_at = "2026-10-05T11:50:32.234919641Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
branch = "bridle/snapshot-tasks"
commit = "8a7ebea"
+++

original id: cru4
docs/tickets/open/tasks-query-counts-the-daily-note-s-due-today-and-overdue-sn-cru4.md

## Thread

### note · external:orchestrator · 2026-10-05T11:50:23.513Z
From orchestrator: approved, merge mn-cru4. Your merge was denied because the chained command didn't match your allowlist (git push -q, git rev-parse aren't allowed; only the exact forms are). Run them as separate plain commands: git merge --no-ff bridle/snapshot-tasks -m "..."; git push origin main; git tag v2.24.1; git push origin v2.24.1; git log -1 --format=%h for the hash; then bridle rm, bridle task done. Leave the ticket move to me (you can't commit; I'll resolve cru4 after the merge). Same for future merges.

### note · agent:manager-1 · 2026-10-05T11:50:32.231Z
integrated: 8a7ebea (branch bridle/snapshot-tasks)

### note · agent:manager-1 · 2026-10-05T11:50:32.234Z
cleanup: removed nothing
