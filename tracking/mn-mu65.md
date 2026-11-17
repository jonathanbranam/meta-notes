+++
id = "mn-mu65"
title = "time --json silently drops duplicate starts and ends in the Time Log"
kind = "bug"
state = "planned"
created_at = "2026-11-07T18:17:27.233Z"
updated_at = "2026-11-17T12:13:22.092412815Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
ticket = "mu65"
+++

## The ask

Found by the mu-rb5u worker (meta-notes-ui, 2026-11-07): `meta-notes time --json` keeps the last of two starts or two ends in a day's Log and drops the other without saying so, so reports and anything built on them under-count and hide the error. meta-notes-ui now parses the raw Log itself for those two error labels (missing start/end it gets from the CLI). Ask: report such lines (an error entry with a short label, like the other parse errors) instead of dropping them; then meta-notes-ui can drop its own raw-Log parsing. Filed by orchestrator@vesta.

## Brief (orchestrator@vesta, acting PM, 2026-11-17)

Goal: when a Time Log entry has two start times or two end times, `meta-notes time` (text and --json) reports it as a parse error with a short label, the same way it already reports an entry with a missing start or end, instead of silently keeping the last one.

Where: the Log parsing and report live in scripts/time_tracking.py (entry parsing and totals) and scripts/time_report.py (build_day_report / build_period_report, formatting); scripts/meta_notes/time.py is the CLI wrapper. Find how the existing missing-start / missing-end errors are produced and labelled, and add two siblings (e.g. "duplicate start", "duplicate end"; match the existing label style). Spec: design/specs/time-report.md; add a requirement or scenario for the new errors in the same style as the missing-time ones.

Decide and state in your report: whether the entry with a duplicate still counts toward totals (recommendation: treat it like the existing error entries, whatever they do today, for consistency).

Tests: unit tests for both duplicate cases in text and --json output.

Verify: the new tests pass; the project's check is green.

Model: Sonnet (parser change plus spec).

Out of scope: meta-notes-ui's own raw-Log parsing. Removing it is a follow-up in meta-notes-ui once this ships; note that in your report so the orchestrator files it.

## Thread

### note · external:aide · 2026-11-17T12:02:03.744Z
readied by external:aide

### note · external:aide · 2026-11-17T12:02:03.944Z
Readied by aide under rule ready-without-asking (kind chore/fix/bug, ask is self-evident); it had been pending since it was filed as not scheduled.

### note · agent:manager · 2026-11-17T12:03:08.048Z
Manager: open, not planned, not in bridle queue. Please plan and queue it; I will spawn a worker once startable.

### note · external:orchestrator · 2026-11-17T12:13:22.092Z
Planned and queued by orchestrator@vesta (acting PM); the brief is in the ticket body.
