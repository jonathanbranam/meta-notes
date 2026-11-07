---
id: mn-mu65
title: time --json silently drops duplicate starts and ends in the Time Log
kind: bug
created: 2026-11-07
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mu-rb5u]
---

## The ask

Found by the mu-rb5u worker (meta-notes-ui, 2026-11-07): `meta-notes time --json` keeps the last of two starts or two ends in a day's Log and drops the other without saying so, so reports and anything built on them under-count and hide the error. meta-notes-ui now parses the raw Log itself for those two error labels (missing start/end it gets from the CLI). Ask: report such lines (an error entry with a short label, like the other parse errors) instead of dropping them; then meta-notes-ui can drop its own raw-Log parsing. Not urgent: the week view works around it. Filed by orchestrator; not scheduled.
