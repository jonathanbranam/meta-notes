---
id: mn-edqk
title: "conventions: when two events claim the same Time Block row, the later-starting event wins it"
kind: fix
created: 2026-11-05
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
resolved: 2026-11-05T14:02:41Z
---

## The ask

From the human by email (m-0195, 2026-11-05, subject "More bug reports to investigate"), filed from the work laptop. The human wrote, verbatim: "More bug reports to investigate and fix." The attachment follows verbatim.

Notes from aide: Rule goes in conventions.md 'Editing the Time Block', next to the mtg:/(opt)/overlap rule from mn-dyer (v2.33.4). Reconcile with that rule's 'ask the user on overlap' wording: this is about the shared boundary row, not about dropping either event.

---

# project/meta-notes/daily-plan skill: end-time row should show the next meeting, not a stale block

For the meta-notes plugin maintainer. Related to
[[project/meta-notes/daily-plan skill - meeting end row is overlap-free, never filled]],
which settled which row counts as a single event's own end-time row.
This ticket is about a different edge: when a *second* event starts at
or near that boundary, is it the one that shows in the shared row.

## Problem

From 2026-10-08's agenda: an "Out of office" calendar block ran through
the afternoon, and a "Consensus Meeting" (an interview) was scheduled
4:05pm–4:30pm, inside that OOO window. Filling the Time Block, the
`4:00pm` row was written as `ooo` instead of the Consensus Meeting,
because the long-running OOO block was still nominally "active" at that
clock time and got filled first/left standing.

The user's correction, stated plainly:

> if meeting A ENDS at 4:05 and meeting B STARTS at 4:05 or 4:10, the
> 4:00 block shows meeting B

## Root cause

The existing convention describes how a single event's own start/end
round onto the grid, but says nothing about priority when two events'
filled ranges would otherwise collide in the same row — one event
"still running" by the clock, another one visibly starting. Readers
(and the agent) default to whichever event they filled first, which
left the earlier, lower-priority OOO block sitting in a row that should
have shown the specific, named meeting someone is about to join.

## Requested rule

When two events' rows would otherwise both claim the same row, the
later-starting event wins that row, since the only thing anyone cares
about at that exact point is which meeting they're walking into — not
which placeholder was already running. State it generally, not just for
OOO:

> When two events' filled rows would otherwise overlap in the same row
> (e.g. event A nominally runs through this row, but event B starts
> partway into it), event B's text wins the row. A later-starting event
> always takes priority over an earlier, still-nominally-running one.

Worked example:

- `OOO 3:00pm–4:30pm` and `Consensus Meeting 4:05pm–4:30pm` → the
  `4:00pm` row shows `Consensus Meeting`, not `OOO` — because by the
  time that row begins, the Consensus Meeting (not the OOO block) is
  the thing actually about to happen.

This likely matters most for broad placeholder events (OOO, Focus time)
that span many rows and would otherwise swallow a specific meeting
nested inside them.

## Suggested change to `scripts/meta_notes/conventions.md`

In "Editing the Time Block," alongside the single-event rounding rule,
add the above rule plus the worked example, so daily-plan doesn't need
to re-derive priority between overlapping events from first principles.

## Note on where this came from

A first pass at writing this up mistakenly went into
`~/.vim/bundle/meta-notes/docs/tickets/open/` (the plugin's own
checkout) instead of here — that's an untracked location in this repo's
git, not the right place for notes-root tickets. Filing here instead,
per the user's correction.


---

## Plan (orchestrator@vesta, acting PM, 2026-11-05)

Haiku. Independent of the other tickets (only conventions.md).

**Change:** in scripts/meta_notes/conventions.md, "Editing the Time Block"
(line ~147), next to the single-event rounding rule and mn-dyer's
mtg:/(opt)/overlap rule, add: when two events' filled rows would claim the
same row, the later-starting event wins that row; with the OOO 3:00-4:30 /
Consensus Meeting 4:05-4:30 example (the 4:00 row shows the meeting).
Reconcile wording with mn-dyer's "ask the user on overlap": this rule only
settles the shared row; it doesn't drop either event or replace the ask.

**Files:** scripts/meta_notes/conventions.md; design/specs/conventions.md
(requirement + the worked example as a scenario) and any test that asserts
conventions text; `__version__` (PATCH) and CHANGELOG.md per
.bridle/rules/versioning.md.

**Verify:** usual check green; the two rules read together without
contradiction.
