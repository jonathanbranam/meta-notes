---
id: mn-n7bd
title: "weekly-plan: lower the capacity threshold (30+ min gaps are capacity, under 30 not listed; ask the user's threshold)"
kind: fix
created: 2026-11-05
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: [mn-8xfd]
---

## The ask

From the human by email (m-0195, 2026-11-05, subject "More bug reports to investigate"), filed from the work laptop. The human wrote, verbatim: "More bug reports to investigate and fix." The attachment follows verbatim.

Notes from aide: Same step of skills/weekly-plan/SKILL.md (step 2, capacity) that mn-8xfd's per-day breakdown builds on; sequence or combine with mn-8xfd so they don't conflict. Where the user's own threshold is kept once asked: the root's CLAUDE.md, not assistant memory (see mn-2pc3).

---

# project/meta-notes/weekly-plan skill: 90min capacity threshold too high

For the meta-notes plugin maintainer. Filed as an issue against the
`weekly-plan` skill (`skills/weekly-plan/SKILL.md` in the plugin repo) —
nothing in this notes repo should be edited to work around it.

## Problem

Step 2 ("Calendar and capacity") says:

> free gaps of 90 minutes or more: these are capacity
> shorter free gaps, listed separately; they aren't capacity

For a week with a schedule like mine (several days close to fully
booked with 25-55 minute meetings back to back), 90 minutes is an
unrealistic bar. Most weeks I never get a single 90-minute gap on 3+ of
the 5 workdays, which makes the "Capacity" total read as near-zero on
those days even though I have several 30-60 minute gaps that are
perfectly usable for the kind of 10-30 minute tasks (feedback requests,
CBTs, quick reviews) that make up a lot of a given week's load.

## Requested rule

Lower the capacity threshold, roughly:

- gaps under 30 minutes: don't track at all — these are just
  back-to-back meeting transition buffers (5-10 min), not real gaps;
  don't even list them in a "short gaps" section
- gaps 30-60 minutes: capacity, but note they're tighter/harder to use
  for deep work
- gaps 60+ minutes: capacity, no caveat

60 minutes is realistically the largest gap I can expect on a normal
week given my meeting load — treating only 90+ as capacity undercounts
real available time by a wide margin. And listing every 5-minute
transition sliver in "Short gaps" adds noise without adding anything
actionable.

## Suggested change to `skills/weekly-plan/SKILL.md`

In step 2, replace the 90-minute line with something like:

> free gaps of 30 minutes or more are capacity (30-60 minutes are
> usable but tighter — call them out as such); gaps under 30 minutes
> are back-to-back transition buffers, not worth listing at all.

Ask the user for their own threshold if it isn't already known, since
this will vary by person and by how granular someone's work tends to
be.


---

## Plan (orchestrator@vesta, acting PM, 2026-11-05)

Haiku. Blocked by mn-8xfd (same step of skills/weekly-plan/SKILL.md; 8xfd's
per-day breakdown uses "whatever threshold is in effect"). Not folded into
8xfd because 8xfd was already queued and may be claimed.

**Change:** in weekly-plan step 2 ("Calendar and capacity"), replace the
90-minute rule: gaps of 30+ minutes are capacity; 30-60 minute gaps are
called out as tighter; gaps under 30 minutes are not listed at all (drop the
short-gap list and update the worked example). If the user's threshold
isn't known, ask; keep their answer in the notes root's `CLAUDE.md` (never
assistant memory, see mn-2pc3) and read it from there next time.

**Files:** skills/weekly-plan/SKILL.md; design/specs/ceremony-skills.md
(the capacity scenario); `__version__` in scripts/meta_notes/__init__.py
(MINOR) and CHANGELOG.md per .bridle/rules/versioning.md.

**Rejected:** a config option or CLI setting for the threshold (YAGNI; the
root's CLAUDE.md already holds user preferences).

**Verify:** usual check green; step 2 reads consistently with 8xfd's
per-day breakdown (which now uses 30 minutes by default).
