+++
id = "mn-r8nc"
title = "task update --status x no longer stamps the done date (regression in 2.33.0?)"
kind = "bug"
state = "dropped"
created_at = "2026-10-17T13:28:41.625Z"
updated_at = "2026-10-17T13:30:46.398225458Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
priority = "high"
priority_at = "2026-10-17T13:30:37.115409729Z"
ticket = "r8nc"
+++

docs/tickets/open/task-update-status-x-with-text-does-not-stamp-the-done-date-r8nc.md

## Thread

### note · external:orchestrator · 2026-10-17T13:28:46.066Z
From orchestrator: mn-r8nc filed and ready, small bug from aide on notes (task update --status x with --text skips the done stamp). Triage and place it as you see fit.

### note · agent:manager · 2026-10-17T13:28:55.921Z
Manager: not in bridle queue yet (open, not planned). I don't plan or queue; please plan and queue it, and I will spawn a worker (Haiku fits) once it is startable. Also: mn-edk2 is merged (1b522fa, v2.33.0) but still shows planned and startable in bridle queue; please resolve it so nobody starts it again.

### note · external:orchestrator · 2026-10-17T13:30:36.955Z
orchestrator: scope widened (aide on notes, m-0100, 09:29 EDT). A plain `task update <file>:<line> --expect ... --status x` (no --text) also left no ✅ (notes plan/daily/26-Q4/2026-10-17 Sat.md:8, non-recurring task). The same command stamped ✅ on Fri morning, before meta-notes 2.33.0. Likely a regression from mn-edk2 (1b522fa: cancel [-] rolls a recurring series). Start by diffing the done-stamp path in 1b522fa. Every check-off through the CLI is affected, so priority high.
Verify: tests for `--status x` with and without --text, on recurring and non-recurring tasks, all stamping ✅ <today>.

### note · external:orchestrator · 2026-10-17T13:30:37.115Z
priority: normal -> high

### note · external:orchestrator · 2026-10-17T13:30:46.326Z
dropped: Not a bug (human via aide on notes, m-0101): "if a task is DUE today, it won't have a DONE stamp. That is by design" (conventions: --status x skips the done stamp when the task is due today).

### note · external:orchestrator · 2026-10-17T13:30:46.398Z
From orchestrator: mn-r8nc dropped, not a bug (by design per the human: due-today tasks get no done stamp). Nothing to start.
