+++
id = "mn-ex6w"
title = "Calendar downloads: a failed move leaves a copy each run; one setting instead of two"
kind = "bug"
state = "integrated"
created_at = "2026-10-08T14:47:32.410Z"
updated_at = "2026-10-08T15:01:31.703428973Z"
created_by = "external:aide"
watchers = ["external:aide"]
priority = "high"
priority_at = "2026-10-08T14:51:20.112341779Z"
commit = "4cf5e5e"
summary = 'Calendar downloads: copy only the newest matching export when newer and its hash matches nothing cached; delete the original if allowed, else leave it; single downloads = "~/Downloads/<glob>" setting, old two keys still read. Item 3 (say when nothing matches) not done, optional. v2.30.0.'
+++

original id: ex6w
docs/tickets/open/calendar-downloads-a-failed-move-leaves-a-copy-each-run-one-ex6w.md

## Thread

### note · external:orchestrator · 2026-10-08T14:51:20.112Z
priority: normal -> high

### note · agent:cal-downloads · 2026-10-08T15:00:56.505Z
Done v2.30.0. Check: vader 184/184 (assertions 458/458), pytest 1623 passed 1 skipped, bridle spec check --require-ids 0 errors. Not done: item 3 (say when nothing matches), YAGNI; only the newest matching file is considered.

### note · agent:manager-2 · 2026-10-08T15:01:31.703Z
integrated: 4cf5e5e
