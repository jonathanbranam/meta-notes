+++
id = "mn-8se5"
title = "Conventions: Actual records only deviations; leave it blank when the plan happened"
kind = "docs"
state = "integrated"
created_at = "2026-10-28T16:33:24.603Z"
updated_at = "2026-10-28T16:46:43.688546088Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
commit = "ba53c7e"
ticket = "8se5"
+++

## Ask

From the human (2026-10-28), via aide (notes), verbatim:

> "As long as actual matches planned, then we don't fill out actual. Because it says 'work' and just
> says 'work' for the planned, and I worked, then we don't need to fill out the actual here. If
> something happens, if I planned it to work and then I go home in the middle of the day for some
> reason, then we would actually fill out the actual, because you only fill out actual if it's
> different. There's no reason to copy the plan into actual, and we have a time log. The time log
> covers in minute detail what happened. The main purpose of actual is to record deviations from
> the plan, so that otherwise they're not visible anywhere else. If that is not clear in the
> meta-notes convention, then please ask the aide to get that clarified."

## Gap

The time-block skill already says "The plan happened: leave Actual blank". But
`scripts/meta_notes/conventions.md`, section `## Editing the Time Block` (what
`meta-notes conventions` prints), only covers rows that "didn't go as planned" and never says to
leave Actual blank when the plan happened. The notes aide copied the Plan into Actual on
2026-10-28 because of this.

## Change

In `## Editing the Time Block` of `scripts/meta_notes/conventions.md`, state outright:

- Actual records only deviations from the Plan and extras not in it.
- A row that went as planned keeps Actual blank.
- Never copy the Plan into Actual.
- The Time Log holds the minute-by-minute detail; Actual is where deviations stay visible.

Keep the existing struck-plan rules as they are. ASCII only. If a test pins the conventions text,
update it; bump the patch version and CHANGELOG per the project's usual practice.

## Verify

`meta-notes conventions` shows the new text; the project's checks pass.

Model: haiku (short docs edit). Out of scope: changing the time-block skill or CLI behaviour.

## Thread

### note · external:orchestrator · 2026-10-28T16:33:38.413Z
From orchestrator: mn-8se5 filed and ready (human's ask via aide, quote on the ticket): short conventions docs fix, haiku. Please plan and schedule it.

### note · agent:manager · 2026-10-28T16:33:40.091Z
Manager: the ask is empty ('The ask' holds only '-'), so I can't brief a worker. Please fill in the ask (what the conventions should say, which files, the human's words) and plan and queue it. Also: mn-yura is merged (d5b3211, v2.33.2) but still shows startable in bridle queue; please resolve it.

### note · external:orchestrator · 2026-10-28T16:34:39.661Z
Orchestrator: ask written into the ticket (e30e17a; my first --body was taken literally as '-'). Will plan and queue when settling ends at 12:43 PM. mn-yura marked integrated (d5b3211).

### note · external:orchestrator · 2026-10-28T16:44:22.084Z
From orchestrator: mn-8se5 now has its ask (e30e17a), is planned and queued in tier 1. Short conventions docs edit, haiku. mn-yura marked integrated.

### note · agent:actual-blank · 2026-10-28T16:45:56.276Z
Done on bridle/actual-blank: 69d2e95. Added the Actual-deviations paragraph to '## Editing the Time Block' in scripts/meta_notes/conventions.md; struck-plan rules unchanged. Version 2.33.3, CHANGELOG entry. vader 190/190, pytest 1632 passed 1 skipped, spec check 0 errors. No spec or test change: design/specs/conventions.md does not cover the Time Block text, and no test pins it.

### note · external:orchestrator · 2026-10-28T16:46:43.688Z
integrated: ba53c7e
