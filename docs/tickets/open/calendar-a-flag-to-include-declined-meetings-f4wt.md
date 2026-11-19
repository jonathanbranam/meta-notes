---
id: mn-f4wt
title: "calendar: a flag to include declined meetings"
kind: feature
created: 2026-11-19
created_by: external:aide
theme: calendar
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

Add a flag to `meta-notes calendar` that includes declined meetings (name up to the implementer, e.g. `--declined`). Default unchanged: declined events stay hidden. With the flag, they appear in text output marked `(declined)` and in `--json` with their `response` value, and the flag works with `--search` and `--with` too. Bump MINOR, update the calendar spec, `:help` and the README.

The human's product decision, by email (m-0409, 2026-11-19, subject "Feature request on calendar functionality"), with this note attached, verbatim:

> # project/meta-notes/Add a flag to include declined meetings in calendar output
> 
> For the meta-notes plugin maintainer.
> 
> ## Problem
> 
> `meta-notes calendar` (and the daily agenda it feeds) silently drops any
> event where the user's own RSVP is `PARTSTAT=DECLINED`. Confirmed today
> by diffing a known-declined meeting against the tool's output:
> "Bi-Weekly: CIDX AI Tools Adoption || Office Hours" on 2026-11-09 13:05
> (`DECLINED` in the raw `.ics`) doesn't appear anywhere in `meta-notes
> calendar --date 2026-11-09 --json` — not in `events`, not in `pruned`,
> not in `warnings`. There's no way to tell, short of unzipping the cached
> export and grepping the raw `.ics` by hand, that the event was ever on
> the calendar for that day.
> 
> This filtering is intentional and already documented as a design
> decision in [[project/meta-notes/Add calendar export to meta-notes]]
> ("Filter out declined events" — default hide, but that note already
> flagged "whether to expose this as a flag... is a product decision").
> This note is that product decision: yes, add the flag.
> 
> ## Why this matters
> 
> A declined event isn't always irrelevant. The user may want to see it
> when reviewing a day or filling in the Time Block — to confirm they're
> not missing something, or because they declined a recurring series by
> default but a specific session has an interesting topic worth attending
> after all. Today the only way to check is dropping into the raw `.ics`,
> which isn't something a skill or a casual lookup should ever need to do.
> 
> ## Requested feature
> 
> Add a flag, e.g. `--declined` (name up to the maintainer), to `meta-notes
> calendar`:
> 
> ```
> meta-notes calendar --date 2026-11-09 --declined
> meta-notes calendar --date 2026-11-09 --declined --json
> ```
> 
> - Default behavior unchanged: declined events stay hidden unless the
>   flag is given.
> - With `--declined`, include them in both the text and `--json` output.
>   The JSON shape already has a `response` field — just stop filtering
>   those events out, so `response: "declined"` (or whatever the existing
>   value is) shows up like any other. The text output should mark them
>   clearly, e.g. `(declined) 1:05pm-1:30pm Bi-Weekly: CIDX AI Tools
>   Adoption || Office Hours`.
> - Should also apply to `--search`/`--with` filtered queries, not just
>   the plain agenda — searching for a meeting by title shouldn't come up
>   empty just because the match was declined.
> 
> ## Related
> 
> - [[project/meta-notes/Add calendar export to meta-notes]] — original
>   design note where the hide-by-default behavior was first decided
> - [[project/meta-notes/Add a calendar event debug command to meta-notes]]
>   — same underlying problem (needing to inspect raw `.ics` fields by
>   hand) for a different reason; a `--declined` flag would cover one of
>   that note's listed debug cases ("was this event filtered out, and by
>   which filter") without needing the full debug command.
