+++
id = "mn-n7bd"
title = "weekly-plan: lower the capacity threshold (30+ min gaps are capacity, under 30 not listed; ask the user's threshold)"
kind = "fix"
state = "integrated"
created_at = "2026-11-05T13:40:06.982Z"
updated_at = "2026-11-05T13:54:31.444467128Z"
created_by = "external:aide"
watchers = ["external:aide"]
commit = "51fd63c"
summary = "Shipped in 2.34.1 (merge 51fd63c): weekly-plan counts 30+ min gaps as capacity (30-60 flagged tighter), drops under-30 gaps, reads/asks the user's 'Capacity gap' from the root's CLAUDE.md."
ticket = "n7bd"
+++

docs/tickets/open/weekly-plan-lower-the-capacity-threshold-30-min-gaps-are-cap-n7bd.md

## Thread

### note · external:orchestrator · 2026-11-05T13:40:48.271Z
Approved for work: the human, via aide (m-0159, relaying email m-0195, 2026-11-05), verbatim: "More bug reports to investigate and fix." and (m-0181) "Please work on them and LMK when the changes have shipped." Readied by orchestrator@vesta.

### note · agent:manager · 2026-11-05T13:40:54.801Z
Manager: not queued yet (open, not planned); please plan and queue it. It edits the same step of skills/weekly-plan/SKILL.md that the running worker weekly-cycle (mn-8xfd) is changing, and I run one worker at a time, so please queue it after mn-8xfd; I will start it once mn-8xfd is merged (to avoid a conflict).

### note · external:orchestrator · 2026-11-05T13:54:30.932Z
integrated: 51fd63c
