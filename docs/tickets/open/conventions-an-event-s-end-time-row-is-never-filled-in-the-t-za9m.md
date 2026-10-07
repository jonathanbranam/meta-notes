---
id: za9m
title: "Conventions: an event's end-time row is never filled in the Time Block"
kind: feature
opened: 2026-10-07
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [y6bw]
tasks: []
---

## The ask

The human, 2026-10-06 (relayed by dalek's bridle aide as m-0547):
"send the contents to meta-notes aide for implementation". The contents are
the note "daily-plan skill - meeting end row is overlap-free, never filled"
from the human's notes root, a follow-up to y6bw (an event fills every Time
Block row it spans). Its substance, quoted:

> While fixing these in today's Time Block, the first attempt wrote each
> meeting through the row matching its literal end time (`1:30pm`,
> `2:30pm`), which the user caught: "a meeting ending at 1:30 isn't in the
> 1:30 block." The next attempt corrected those two but then overcorrected
> a third meeting (`16:05–16:30`) by rounding its *start* down past the
> row it belongs in, extending it one row too far in the other direction
> (filling `4:00pm` through `4:30pm` instead of stopping at `4:15pm`).

> State the end boundary as exclusive, and give enough worked examples
> that both the "ends mid-row" and "ends exactly on a row boundary" cases
> are unambiguous:
>
> > An event fills the Plan of every 15-minute row during which any part
> > of it is happening. Round the start down to the row it falls in. The
> > row beginning exactly at the event's end time is never filled, since
> > no part of the event is still happening once that row begins.
>
> Examples (15-minute grid):
>
> - `9:00–10:00` → fills `9:00am, 9:15am, 9:30am, 9:45am` (`10:00am` is not
>   filled; the meeting is already over by then)
> - `10:05–10:30` → fills `10:00am, 10:15am` (`10:30am` is not filled)
> - `10:35–11:25` → fills `10:30am, 10:45am, 11:00am, 11:15am` (`11:30am`
>   is not filled)
> - `13:05–13:30` → fills `1:00pm, 1:15pm` (`1:30pm` is not filled)
> - `16:05–16:30` → fills `4:00pm, 4:15pm` (`4:30pm` is not filled)
> - `2:00–2:30` (already on row boundaries) → fills `2:00pm, 2:15pm`
>   (`2:30pm` is not filled)
> - `11:50–12:05` (a short meeting spanning one grid line) → fills
>   `11:45am, 12:00pm` (`12:15pm` is not filled)
>
> The rule in one sentence: **the end-time row is never filled**, no
> matter how it aligns to the grid — only rows where the meeting is still
> actively running get the text.

> In "Editing the Time Block," replace the rounding sentence ... with the
> wording above (rule + the full example list), so an implementer or an
> assistant following the convention doesn't have to re-derive the
> exclusive-end behavior from first principles.

Where: the event paragraph in "Editing the Time Block" in
`scripts/meta_notes/conventions.md` (it says an event "fills the Plan of
every row it spans" but not which row is last). Worth saying alongside it
that `--through` names the last filled row (the row before the end time),
as the existing `--time 7:00pm --through 8:45pm` example already implies.
Docs text only; update `test_conventions.py` if it pins the text. Version
per `.bridle/rules/versioning.md`.
