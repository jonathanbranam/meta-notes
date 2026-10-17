---
id: mn-r8nc
title: "task update: --status x with --text does not stamp the done date"
kind: bug
created: 2026-10-17
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
resolved: 2026-10-17T13:30:54Z
---

## The ask

Reported by aide on notes (m-0098, 2026-10-17), while working the human's daily note.

`meta-notes task update <file>:<line> --expect ... --status x --text "..."` marked the task `[x]`
but did not add the `✅ <today>` done stamp. `--status x` alone stamps it. Seen on
`plan/daily/26-Q4/2026-10-17 Sat.md:7`, meta-notes 2.33.x; aide added the stamp by hand.

Expected: `--status x` stamps the done date whether or not `--text` is also given (and a
`--text` that already carries a `✅` date keeps it, no double stamp).

Verify: a test for `--status x --text ...` producing the stamp; `just check` green.
Model: Haiku or Sonnet, small fix in the task update path.
