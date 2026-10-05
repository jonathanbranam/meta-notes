---
id: y6bw
title: "Conventions: an event fills every Time Block row it spans, travel included"
kind: feature
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

The human, 2026-10-04 (relayed by the notes advisor), for the time-block
and daily-plan skills:

> When there's something happening, like an event that's going on, it
> should fill the plan for the time that it takes. Driving to the concert
> takes 30 minutes. I should say: the 30 mark leads to the concert, and at
> the 45, driving to the concert. If the concert is 1.5 hours (I guess I
> didn't specify exactly how long it was), those plan blocks should be
> filled with watching the concert or something like that.

So: an event (meeting, concert, appointment, errand) fills the Plan of
every row it spans, not just its first row; travel to and from it is its
own run of rows ("drive to concert" in each 15-minute row it takes), and
the event's rows follow ("concert"). With no known end, use a typical
length and say so to the user, or ask. One `time-block update --time X
--through Y --plan '<text>'` writes the run.

Where: the Editing the Time Block section of
`scripts/meta_notes/conventions.md` (both skills read it via
`meta-notes conventions`), and daily-plan step 5 ("place every meeting
... at its times") and the time-block skill point to it. The human has a
copy in the notes CLAUDE.md (My day) for now; tell the notes advisor
when it ships so it can be removed there. Docs and skill text only; test
`test_conventions.py` if it pins the text. Minor version.
