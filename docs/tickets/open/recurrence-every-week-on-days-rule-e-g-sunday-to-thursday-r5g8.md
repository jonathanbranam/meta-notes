---
id: mn-r5g8
title: "Recurrence: 'every week on <days>' rule (e.g. Sunday to Thursday)"
kind: feature
created: 2026-11-08
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

The human, 2026-11-08 (via aide, m-0200, verbatim): "it should really be a Sun-Thr task but idk if that's possible". Aide's ask: support Obsidian Tasks' `every week on <days>` rule.

## Problem
`meta-notes task update --recur 'every week on Sunday, Monday, Tuesday, Wednesday, Thursday'` is rejected: scripts/recurrence.py only parses `every N days/weeks/months/years` (optional `when done`) and `every weekday`. Workaround in place: five weekly tasks in area/home/Home.md (the human can collapse them to one after this lands; not part of this ticket).

## Ask
Parse and complete `every week on <day>[, <day>...]` as Obsidian Tasks writes it (day names, comma separated, `and` before the last if Obsidian allows it; case-insensitive), with optional `when done`. Also `every N weeks on <days>` if it falls out naturally (Obsidian supports it); skip if it adds real complexity.

## Design
- scripts/recurrence.py: a new rule form holding the set of weekdays; `next_date` returns the next listed day after the base date (for `every N weeks on`, the next listed day in the current week, else the first listed day N weeks on).
- Everything that uses parse_rule/next_date (task update --recur, completing a recurring task and spawning the next, `--at` queries, the report in tasks.py) works with it unchanged or with the smallest change.
- Write the rule back exactly as the user gave it (the Obsidian plugin must still read it).

## Files likely
scripts/recurrence.py, scripts/tasks.py (if it reports rules), test/unit/test_recurrence.py, test/unit/test_task_update.py, the recurrence spec/docs and the prime guide if they list the supported forms.

## Check
The project's check green; unit tests for parsing (valid and invalid day lists), next_date across week ends (Thursday -> Sunday), and completing a `every week on Sunday, Monday, Tuesday, Wednesday, Thursday` task spawning the right next date.

## Model
Haiku (small parser change with clear tests).

## Not in this ticket
Other Obsidian forms (every month on the 1st, every last Friday). Rewriting the human's five workaround tasks.
