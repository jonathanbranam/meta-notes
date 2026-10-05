---
id: vcey
title: "Agenda preset: overdue, today and each day ahead in one task query"
kind: feature
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [cru4]
tasks: [mn-kbfa]
closed: 2026-10-05T23:18:50Z
---

## The ask

The human, 2026-10-05 (relayed by the notes advisor, notes m-0076): "I want
to make it really easy for you to run a command that gets you the exact
information you want." The notes advisor now checks tasks at every startup:
overdue, due today, then each day ahead, at least 5 days and through the
next Monday (Thursday or Friday: through the following Wednesday), and
undated tasks at some cadence ("those could be coming up due and be
something I've overlooked").

## Today

`meta-notes tasks --overdue --due --ready --date 2026-10-05..2026-10-12`
gets the right set in one call, but:

- `--date` takes no relative dates, so the agent works out the horizon;
- the Due section isn't split by day, so today mixes with next Saturday;
- today's timed tasks move to Overdue once their time passes unless
  `--at` is given;
- started-not-due tasks (🛫) need `--ready`;
- the daily-note snapshot copies inflate everything until
  [[docs/tickets/resolved/tasks-query-counts-the-daily-note-s-due-today-and-overdue-sn-cru4|cru4]] merges.

## Suggestion (the advisor's)

One preset, `meta-notes tasks --agenda` (or `meta-notes agenda`): Overdue,
Today, then one section per following day through the horizon rule above,
optionally Undated; `--json` too. Open points for the human: the horizon
rule as a default or `--through`; whether a work root (much longer lists)
needs it narrowed; whether today's passed timed tasks stay under Today.

## Decision

The human approved the ticket as written, 2026-10-05 (relayed by the notes
advisor). The orchestrator settled the open points in task mn-kbfa's brief:
`tasks --agenda`, the horizon rule as the default with `--through DATE` to
override, the same in work and personal roots, today's passed timed tasks
stay under Today, and `--undated` adds an Undated section (off by default).
The worker records the behaviour in `design/specs/task-query.md`.
