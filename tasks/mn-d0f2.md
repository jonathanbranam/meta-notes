+++
id = "mn-d0f2"
title = "Fix autoreload: timer never starts, reload notice never shows"
kind = "bug"
state = "integrated"
created_at = "2026-10-01T19:48:53.861Z"
updated_at = "2026-10-01T19:50:24.530035088Z"
branch = "bridle/reload-fix"
commit = "9518ee7"
summary = "Autoreload fixes: the timer now starts from Attach (idempotent); the reload notice now shows from FileChangedShellPost unless the reason is mode/time. Spec and vader updated; ticket moved to resolved. Version 2.8.1, merged 9518ee7, tagged v2.8.1. Not testable headlessly: the real watcher-driven reload with autoread, and the timer actually firing a reload."
+++

Ticket docs/tickets/open/autoreload-timer-and-notice-bugs-6p68.md has both causes and fixes. PATCH bump; move the ticket to resolved in the branch. Message the manager your check results.

## Thread

### note · agent:manager · 2026-10-01T19:50:22.499Z
integrated: 9518ee7 (branch bridle/reload-fix)

### note · agent:manager · 2026-10-01T19:50:22.505Z
cleanup: removed nothing
