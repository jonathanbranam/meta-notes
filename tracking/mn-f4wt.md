+++
id = "mn-f4wt"
title = "calendar: a flag to include declined meetings"
kind = "feature"
state = "integrated"
created_at = "2026-11-19T11:46:11.784Z"
updated_at = "2026-11-19T12:01:19.764882416Z"
created_by = "external:aide"
watchers = ["external:aide"]
commit = "d841e98"
summary = "calendar --declined (3.2.0, d841e98): lists declined meetings, '(declined) ' prefix in text, response 'no' in --json; works with --search/--with. Default unchanged."
ticket = "f4wt"
+++

docs/tickets/open/calendar-a-flag-to-include-declined-meetings-f4wt.md

## Thread

### note · external:aide · 2026-11-19T11:46:22.480Z
readied by external:aide

### note · external:aide · 2026-11-19T11:46:22.730Z
Readied by aide: a feature, but the human made the product decision in the mail itself ("This note is that product decision: yes, add the flag"), so the ask is self-evident.

### note · agent:manager · 2026-11-19T11:46:26.922Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once startable.

### note · external:orchestrator · 2026-11-19T11:58:02.051Z
Planned and queued by orchestrator. Brief: the ask above stands. Model: Sonnet (small feature, but touches the event filter shared by --search/--with). Verify: just check green; a test that a DECLINED fixture event is hidden by default and shown with the flag in text (marked (declined)), --json (response field), and with --search/--with. Out of scope: the calendar debug command.

### note · external:orchestrator · 2026-11-19T12:01:12.055Z
integrated: d841e98

### note · external:orchestrator · 2026-11-19T12:01:19.764Z
Orchestrator: read the diff (calendar.py, cli.py, tests), resolved in ef53290, marked integrated at d841e98. Note: --json shows response 'no' (the existing decline value), not 'declined'.
