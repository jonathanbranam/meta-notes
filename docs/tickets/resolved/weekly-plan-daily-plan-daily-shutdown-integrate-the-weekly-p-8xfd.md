---
id: mn-8xfd
title: "weekly-plan, daily-plan, daily-shutdown: integrate the weekly plan into the daily cycle (per-day breakdown, daily read, shutdown write-back, at-risk check, meetings first)"
kind: feature
created: 2026-11-05
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
resolved: 2026-11-05T13:44:28Z
---

## The ask

From the human by email (m-0181, 2026-11-05, subject "some bug reports to address"), filed from the work laptop. The human asked, verbatim: "Please work on them and LMK when the changes have shipped." The attachment follows verbatim.

Notes from aide:
- Item 5 supersedes the placement done in mn-bf7a (meetings filled in step 5 of daily-plan): move the meeting fill to right after picking the target day.
- Item 1 mentions an "already-filed `weekly-plan skill - 90min capacity threshold too high` note". That note lives in the human's work notes; it was never filed here, and weekly-plan still uses 90-minute gaps (skills/weekly-plan/SKILL.md:70). Not part of this ticket unless the human says so.
- Personal roots (Sunday weekly plan, no daily shutdown) need a sensible behaviour too.

---

# project/meta-notes/weekly-plan, daily-plan, daily-shutdown: integrate the weekly plan into the daily cycle

For the meta-notes plugin maintainer. This is a request to change three
shipped skills — `skills/weekly-plan/SKILL.md`,
`skills/daily-plan/SKILL.md`, and `skills/daily-shutdown/SKILL.md` in the
plugin repo — so the weekly plan and the daily plan/shutdown cycle
actually talk to each other. Nothing in this notes repo should be edited
to work around it.

## Problem: the weekly plan and the daily cycle don't talk to each other

Today, as shipped:

- `weekly-plan` writes a flat list of priorities and deadlines once, for
  the whole week, without assigning any of them to a specific day.
- `daily-plan` reads the week note's `## Plan` section only when the
  target day is a Monday, and even then only as one-time input — it
  never checks it again later in the week, and never writes back to it.
- `daily-shutdown` never reads or writes the week note at all.

The practical effect: the weekly plan is a write-once document. By
Wednesday it no longer reflects what's actually been done, what slipped,
or what new work has shown up mid-week, and nothing in the daily cycle
keeps it current or checks progress against it. All of the reconciling —
"is this still on track for Friday?", "where did this new work item go?",
"what's actually left from Monday's plan?" — has to happen by hand, in
conversation, every single day.

This week (anonymized) is a representative example: Monday's weekly plan
set a short list of priorities and deadlines for the week. By Wednesday,
several new work items had come up over the course of planning and
shutdown conversations (quick asks from teammates, follow-ups from
meetings) that didn't exist when the weekly plan was written. Each had to
be manually triaged — decide which day it realistically fits, update its
due date, and by hand add a line to the week note's `## Plan` /
`### Deadlines` section so it wouldn't be forgotten. None of that
reconciliation was something either skill did on its own; it only
happened because a human (with an assistant) noticed the mismatch and
fixed it conversationally. The five requests below are aimed at making
that reconciliation automatic.

## 1. `weekly-plan`: assign work to specific days, not just a flat list

### Problem

`weekly-plan`'s output (the `### Priorities` / `### Deadlines` sections)
is one undifferentiated list for the whole week. It doesn't look at how
much open time each day actually has and doesn't map any priority to a
specific day. Two days in the same week can have very different
capacity — one day packed with back-to-back 25-55 minute meetings,
another with several open 60+ minute blocks — but the weekly plan treats
every day the same way: everything just goes in one list, and figuring
out "what should happen today vs. later this week" is left entirely to
the daily conversation.

### Requested change

In its capacity/calendar step, after computing each day's open time
(using whatever capacity threshold is in effect — see the related,
already-filed `weekly-plan skill - 90min capacity threshold too high`
note), do a rough first-pass assignment of the week's priorities and
deadlines to specific days, based on each day's capacity and each item's
rough size/urgency. Write this as a per-day breakdown in the week note's
`## Plan` section (for example, a short list under each remaining
workday) rather than one combined list with no day attached. It doesn't
need to be precise — the daily-plan/shutdown changes below are what keep
it honest as the week actually unfolds — but it should give each day a
starting point instead of an empty slate.

## 2. `daily-plan`: read the weekly plan every day, not just Monday

### Problem

Step 2 of `daily-plan` only reads the week note's `## Plan` section "when
TARGET is a Monday." On any other day it's not consulted at all, so a
Wednesday or Thursday planning session has no visibility into what the
week's plan assigned to that day, what's already been marked done, or
what's still pending from earlier in the week.

### Requested change

On every day, not just Monday, `daily-plan` should read the week note's
`## Plan` section (specifically, once request #1 above exists, that
day's slice of the per-day breakdown) to see what was assigned to today
and what's still open from earlier days. Reconcile this against today's
actual due-dated tasks (the existing `tasks --due`/`--overdue` queries)
rather than treating the week note and the task system as two unrelated
sources of truth.

## 3. `daily-shutdown`: write actual progress back into the weekly plan

### Problem

`daily-shutdown` never touches the week note. At the end of a day,
several things typically happen that the weekly plan should know about:
some assigned work got done, some didn't and needs to move to a later
day, and new work appeared that wasn't in the plan at all. Today all of
that just lives in the daily note's own `## Follow Up` list and task due
dates; the week note's per-day breakdown (once #1 exists) would
otherwise go stale the same day it was written, since nothing updates it.

### Requested change

As part of (or right after) the existing Follow Up step,
`daily-shutdown` should update the week note's per-day `## Plan`
breakdown: mark today's assigned items that got done, and move anything
unfinished — plus any new work captured during the day that didn't fit —
onto a later day in the same breakdown, consistent with whatever gets
written to Follow Up / task due dates anyway. The goal is that the week
note's per-day plan is never more than one day stale.

## 4. `daily-plan`: call out weekly commitments at risk

### Problem

Nothing currently checks whether a day's calendar and workload leave
realistic room for what the week's plan expects to happen that day (or
by a deadline later in the week). This week, a day with a nearly fully
booked calendar also had several new work items added during the
planning conversation itself; the total due-that-day workload clearly
exceeded the day's actual open blocks, but nothing flagged this — it
only became visible because a human looked at the numbers (total open
minutes vs. total requested work) and asked which items should actually
happen today vs. slip. The skill has all the inputs needed to notice
this itself (calendar, capacity, due dates) but doesn't use them for this
check.

### Requested change

After filling the Time Block (see #5) and gathering due work, `daily-plan`
should compare today's (and this week's upcoming) committed/assigned
work against the day's actual remaining open time. If a weekly priority
or deadline assigned to today — or coming due later this week — doesn't
realistically fit, say so explicitly to the user (e.g. "today's open time
is about 2 hours; the items assigned to today add up to more than that —
which should slip?") rather than silently proceeding as if everything
will get done.

## 5. `daily-plan`: fill the Time Block from the calendar as the literal first step

### Problem

A related, already-filed note (`daily-plan skill - fill Time Block from
meetings by default`) asked for meetings to be placed in the Time Block
before other work, as part of step 5 ("Write the plan"). In practice
that's still fairly late in the skill's flow — target day, previous-day
review, outlook, meetings-in-prose, due/overdue/waiting tasks are all
gathered and discussed *before* the Time Block table itself gets
written. The user doesn't see the actual visual shape of the day (which
hours are already spoken for vs. genuinely open) until most of the
planning conversation has already happened.

### Requested change

Reorder the skill so that, immediately after picking the target day
(current step 1), `daily-plan`'s very next action is to fetch the
calendar and write every meeting straight into the Time Block table —
before outlook, before due/overdue/waiting tasks, before any other
gathering or conversation. This supersedes the earlier request's
placement (which put the meeting-fill inside step 5) by moving the same
behavior to the front of the whole skill: the user should be able to
glance at the note and see today's meeting skeleton almost immediately,
then have the rest of planning (including the open-time-vs-workload
check in #4) build on that already-visible structure instead of
reconstructing it from scratch at the end.

---

## Plan (orchestrator@vesta, acting PM, 2026-11-05)

One ticket, one worker, Sonnet. The five parts share one data shape (the
per-day breakdown in the week note's `## Plan`), so splitting would make two
workers agree on that shape across a merge boundary; one coherent change is
cheaper.

**Goal.** The week note's `## Plan` gets a per-day breakdown that weekly-plan
writes, daily-plan reads every day, and daily-shutdown keeps current, with
daily-plan putting meetings in the Time Block first and flagging work that
doesn't fit.

**Files it may touch (impact list):**
- `skills/weekly-plan/SKILL.md` (part 1)
- `skills/daily-plan/SKILL.md` (parts 2, 4, 5)
- `skills/daily-shutdown/SKILL.md` (part 3)
- `design/specs/ceremony-skills.md` (requirements/scenarios for the new
  behaviour; follow `.bridle/rules/specs.md`), and any skill tests that
  already cover these skills
- `scripts/meta_notes/__init__.py` (`__version__`, MINOR bump: new skill
  behaviour) and `CHANGELOG.md` (one or two user-facing lines), per
  `.bridle/rules/versioning.md`
- Templates under `templates/` only if a week-note template defines
  `## Plan` and needs the per-day layout.

**Design decisions:**
- Per-day breakdown: under the week note's `## Plan`, one `### <Weekday>
  <YYYY-MM-DD>` heading per remaining day of the plan's week, each with a
  checkbox list. Keep the existing `### Priorities` / `### Deadlines` as the
  week-level view; the per-day lists point at them, not duplicate prose.
  The worker may adjust the exact headings if the specs or conventions
  already fix a form; say so in the report.
- Part 1 is rough on purpose: assign by each day's open time (whatever gap
  threshold is in effect; 90 min today) and item urgency.
- Part 2: daily-plan reads today's slice plus unchecked items from earlier
  days on every day, and reconciles them with the `tasks --due/--overdue`
  results (one combined list; say which came from where only where they
  disagree).
- Part 3: daily-shutdown, in or right after its Follow Up step, checks off
  done items for today and moves unfinished and new items to a later day in
  the same breakdown, consistent with Follow Up and due dates.
- Part 4: after the Time Block and due work are known, compare assigned or
  due work against remaining open time; if it doesn't fit, tell the user
  plainly with the numbers and ask what slips. Don't silently proceed.
- Part 5: the meeting fill from mn-bf7a moves from step 5 to right after
  picking the target day; nothing else in mn-bf7a changes.
- Personal roots (Sunday weekly plan, no daily shutdown): the breakdown
  covers the plan's own week as configured (Sunday start); daily-plan still
  reads it; with no daily-shutdown, the next daily-plan does the catch-up
  (checks off what's done per the previous day's note, rolls unchecked
  items forward) so the breakdown stays at most a day stale.
- If a week note has no per-day breakdown (older weeks), the skills fall
  back to today's behaviour and don't rewrite the note's structure.

**Rejected:** two tickets (manager's suggestion), for the shared-shape
reason above. Making daily-plan create the breakdown on the fly when
missing: more behaviour than asked; weekly-plan owns it.

**Deferred (not yet):** the 90-minute capacity threshold change. The human's
note about it lives in their work notes and was never filed here; not part
of this ticket unless the human asks.

**Verify:** the worker's usual check (pytest and `run_tests.sh` where they
apply) green; the spec scenarios for parts 1-5 and the personal-root case are
present; read the three SKILL.md files end to end for a consistent step order
(daily-plan: target day, then Time Block meetings, then the rest).
