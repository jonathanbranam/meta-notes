+++
id = "mn-edk2"
title = "Cancelling a recurring task doesn't create its next occurrence"
kind = "bug"
state = "planned"
created_at = "2026-10-17T01:47:28.740Z"
updated_at = "2026-10-17T02:41:52.716485209Z"
created_by = "external:orchestrator@vesta"
watchers = ["external:orchestrator@vesta"]
ticket = "edk2"
+++

docs/tickets/open/cancelling-a-recurring-task-doesn-t-create-its-next-occurren-edk2.md

## Thread

### note · agent:manager · 2026-10-17T02:01:01.319Z
Manager: marked ready on the orchestrator's request (human's approval is quoted under Approval). Planning and queueing are the orchestrator's; I will spawn a Haiku worker once it is startable in bridle queue.

### note · agent:recur-cancel · 2026-10-17T02:41:52.716Z
Built the first option on bridle/recur-cancel (2d7f6c0): --status - on a recurring task rolls the series like x; --no-recur ends it for x or -. Version 2.33.0, CHANGELOG, task-update spec (new scenarios: Canceled again, Canceled series ends), doc/meta-notes.txt. Vader 190/190 (478 assertions), pytest 1628 passed, 1 skipped; bridle spec check --require-ids: 31 files, 0 errors.
