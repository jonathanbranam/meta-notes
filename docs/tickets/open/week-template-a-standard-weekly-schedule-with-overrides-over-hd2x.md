---
id: hd2x
title: "Week template: a standard weekly schedule with overrides, overlaid on daily plans"
kind: explore
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [m6jy, zyab, u34c]
tasks: []
---

## The ask

The human, 2026-10-05 (relayed by the notes advisor, notes m-0071; bracketed
names are the advisor's reading of dictation):

> we should have a consistent way to set a week template in this repo. This
> isn't a bridle thing. This is a notes repo or meta notes thing. We have
> recurrences in meta notes, but they're for tasks, not for the regular
> calendar occurrences. We should explore that system and see if we can
> extend the task system, or possibly with a different syntax. I don't want
> to overload the task system necessarily, but we could come up with
> something that would indicate a standard weekly schedule like this. I would
> want to be able to overlay it and override it with special things like
> [Esther] has tap and tumbling every week (the two dance classes). Esther
> has piano every week. [Zeal] has violin every week. ... on some of those
> days, my mom picks them up and brings them to me at work, and then I take
> them home. On some of the other days, I pick up Esther. What I mean about
> overrides is that I want to be able to layer in holidays and school breaks
> and things. Calendar integration may be the solution here ... I have these
> [Esther's] dance classes on my calendar, but the other things are kind of
> routine things that don't really fit as events on a calendar.

Their routine so far is in the personal notes root's `CLAUDE.md`,
`## Daily routine` (up 6:45, school run, work 8:00 to 5 or 6).

## Today

- `🔁` recurrence (`scripts/recurrence.py`) is for tasks: one line in a home
  note, completed and regenerated. No weekday choice (`every week on Tue`),
  no duration, and a routine isn't something you check off.
- `meta-notes calendar` reads a Google export; live access is
  [[docs/tickets/open/live-calendar-access-read-google-and-cozi-carefully-scoped-w-m6jy|m6jy]].
- The daily note's Time Block Plan column starts empty; `daily-plan` fills it.

## Options

1. **A week template note** (recommended). One note in the root, e.g.
   `area/week-template.md`, a section per weekday listing routine blocks
   (`- 3:30pm-4:30pm Esther piano; Mom picks up, brings to work`). Overrides
   in the same note as dated ranges (`- 2026-12-21..2027-01-02 school break:
   no school runs, no lessons`) and one-off dates. Plain markdown, no new
   task semantics.
   - Step 1 (no code): `daily-plan` and `weekly-plan` read the note and put
     its blocks into the Time Block, applying overrides. Proves the shape.
   - Step 2, if step 1 sticks: `meta-notes week-template --date <day> --json`
     resolves a day's blocks (template plus overrides) so skills and
     meta-notes-ui don't each parse it; maybe `note daily` pre-fills Plan.
2. **Extend task recurrence** (`🔁 every week on Tue,Thu` plus `⏰` time and
   a duration). Reuses parsing, but routines would show in task queries and
   need "completing"; the human doesn't want to overload tasks.
3. **Calendar only.** Put routines on Google/Cozi as recurring events and
   read them via m6jy. Overrides come free from the calendar, but the human
   says routines don't fit as calendar events, and it waits on m6jy.

Calendar events (Esther's dance) overlay any option once m6jy lands;
holidays and school breaks could later come from a school calendar feed
instead of hand-entered ranges.

## Not ready

Explore ticket, no task. Needs the human's pick of option and, for option 1,
the note's location and line format.
