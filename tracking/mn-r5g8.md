+++
id = "mn-r5g8"
title = "Recurrence: 'every week on <days>' rule (e.g. Sunday to Thursday)"
kind = "feature"
state = "integrated"
created_at = "2026-11-08T13:40:20.835Z"
updated_at = "2026-11-08T13:55:20.716206476Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
branch = "bridle/recur-days"
commit = "0684215"
summary = "scripts/recurrence.py parses 'every [N] week[s] on <days>' (full day names, comma or 'and', case-insensitive, optional 'when done'); next_date returns the next listed day, else the first listed day N weeks on. Merged 0684215, v2.36.0. Orchestrator check: read the merge diff, ran parse_rule and next_date on the Sun-Thu rule (Sun Mon Tue Wed Thu, then Sun). Full check not re-run: worker reported vader 190/190, pytest 1712 passed 1 skipped, spec check 0 errors."
ticket = "r5g8"
+++

docs/tickets/open/recurrence-every-week-on-days-rule-e-g-sunday-to-thursday-r5g8.md

## Thread

### note · agent:manager · 2026-11-08T13:40:48.313Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once it is startable.

### note · agent:recur-days · 2026-11-08T13:54:24.586Z
Built on bridle/recur-days (95eb737, merged with local main, no new main commits). scripts/recurrence.py parses 'every [N] week[s] on <days>' (full day names, comma or 'and', optional when done); next_date gives the next listed day, wrapping into the next week. Spec recurrence.md (new scenarios), conventions and doc text, CLI --recur error text. Version 2.36.0 (MINOR), CHANGELOG entry. Check: vader 190/190 (478 assertions), pytest 1712 passed 1 skipped, bridle spec check --require-ids 0 errors.

### note · external:orchestrator · 2026-11-08T13:55:20.451Z
integrated: 0684215 (branch bridle/recur-days)

### note · external:orchestrator · 2026-11-08T13:55:20.456Z
cleanup: removed nothing
