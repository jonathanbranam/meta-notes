+++
id = "mn-r5g8"
title = "Recurrence: 'every week on <days>' rule (e.g. Sunday to Thursday)"
kind = "feature"
state = "planned"
created_at = "2026-11-08T13:40:20.835Z"
updated_at = "2026-11-08T13:54:24.586872808Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "r5g8"
+++

docs/tickets/open/recurrence-every-week-on-days-rule-e-g-sunday-to-thursday-r5g8.md

## Thread

### note · agent:manager · 2026-11-08T13:40:48.313Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable.

### note · agent:recur-days · 2026-11-08T13:54:24.586Z
Built on bridle/recur-days (95eb737, merged with local main, no new main commits). scripts/recurrence.py parses 'every [N] week[s] on <days>' (full day names, comma or 'and', optional when done); next_date gives the next listed day, wrapping into the next week. Spec recurrence.md (new scenarios), conventions and doc text, CLI --recur error text. Version 2.36.0 (MINOR), CHANGELOG entry. Check: vader 190/190 (478 assertions), pytest 1712 passed 1 skipped, bridle spec check --require-ids 0 errors.
