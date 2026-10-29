---
id: mn-dyer
title: "conventions: add the mtg:/(opt) prefix and overlap-ask rules for Time Block meetings (moved from daily-plan)"
kind: bug
created: 2026-10-29
created_by: external:aide
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

The human, 2026-10-29 10:04 AM ET, by email (m-0165, subject "Issue with
missing meta-notes conventions"), verbatim:

> Please fix this:

with this attachment (written in their notes root; quoted in full below).

Confirmed by aide: `skills/daily-plan/SKILL.md:136-138` has the `mtg:` /
`(opt) ` rule and the overlap rule; `scripts/meta_notes/conventions.md`
has neither.

## Changes

- `scripts/meta_notes/conventions.md`, "Editing the Time Block": after the
  event fill-rule examples, add the `mtg: <title>` / `(opt) mtg: <title>`
  rule and the overlap-ask rule (suggested text in the attachment).
- `skills/daily-plan/SKILL.md` step 5: replace the two bullets with a
  pointer to `meta-notes conventions`, as step 5 already does for the fill
  rule.
- Tests that pin the conventions text; patch release with a CHANGELOG entry.

## Verify

`meta-notes conventions` (and `prime`) print the `mtg:`/`(opt)` and overlap
rules; `daily-plan` no longer duplicates them; `just check` green.

## The attachment, verbatim

> # project/meta-notes/meta-notes conventions: missing `mtg:` prefix and `(opt)`/overlap rules
> 
> For the meta-notes plugin maintainer. Filed as an issue against
> `scripts/meta_notes/conventions.md` (the text `meta-notes conventions`
> prints) — nothing in this notes repo should be edited to work around it.
> 
> ## Problem
> 
> `skills/daily-plan/SKILL.md` step 5 already documents, in detail, how a
> meeting should be written into a Time Block Plan cell:
> 
> > - An event's `response` is `yes`, `maybe`, `no-reply`, or null (see the
> >   `calendar` skill, which also documents `mine`). Write `yes` meetings
> >   plainly; prefix the others with `(opt) `, e.g. `(opt) mtg: X`.
> > - When events' `start`–`end` ranges intersect, tell the user and ask
> >   which to keep, or whether to note both (`mtg: X / (opt) mtg: Y`).
> >   Never drop one silently.
> 
> That's the fix from
> [[project/meta-notes/daily-plan skill - fill Time Block from meetings by default]]
> (marked `fixed`), and it is in fact in the shipped `daily-plan`
> `SKILL.md` now. But `meta-notes conventions` — the shared reference that
> `daily-plan` step 2 itself says to "run ... and follow it for
> everything below," and that every other skill and a plain assistant
> session relies on for Time Block formatting — only has the generic
> fill-rule text (round start down, exclusive end row, with examples). It
> says nothing about the `mtg:` prefix or the `(opt) ` marker for
> `maybe`/`no-reply`/null responses, and nothing about asking the user
> before resolving an overlap instead of picking silently.
> 
> Concretely, today (2026-10-29) the user asked directly ("run `meta-notes
> prime` then write out my time block for today, only include calendar
> events") without going through the `daily-plan` skill. The assistant
> read `meta-notes prime` and `meta-notes conventions` only, found no
> mention of `mtg:`/`(opt)`, and wrote plain meeting titles with an
> improvised trailing `(opt)` suffix (e.g. `fuel station (opt)`) instead
> of the prescribed leading `(opt) mtg: Fuel Station`. The user had to
> point out the convention was missing and ask whether it was a
> `meta-notes prime`/`conventions` bug.
> 
> ## Root cause
> 
> The `mtg:`/`(opt)` formatting and the overlap-ask rule live only in
> `daily-plan`'s `SKILL.md`, not in `conventions.md`. Anything that fills
> a Time Block Plan cell from calendar events — not just the `daily-plan`
> skill — needs this rule, but `conventions.md` is the only reference
> that's always loaded (`meta-notes prime`) regardless of which skill, if
> any, is running.
> 
> ## Requested rule
> 
> Move the two bullets above (prefix convention + overlap handling) out of
> `daily-plan`'s `SKILL.md` and into `conventions.md`'s "Editing the Time
> Block" section, right after the existing event-fill-rule paragraph and
> examples. Leave a cross-reference in `daily-plan`'s `SKILL.md` ("see
> `meta-notes conventions`") in place of the duplicated text, the way step
> 5 already does for the fill rule itself.
> 
> ## Suggested change to `scripts/meta_notes/conventions.md`
> 
> In "Editing the Time Block," after the existing fill-rule examples, add:
> 
> > Write a calendar meeting's Plan text as `mtg: <title>`. An event whose
> > `response` is `maybe`, `no-reply`, or null gets a leading `(opt) `
> > (`(opt) mtg: <title>`); only `response: "yes"` meetings are written
> > plain. When two events' `start`–`end` ranges intersect, tell the user
> > and ask which to keep, or whether to note both
> > (`mtg: X / (opt) mtg: Y`) — never drop one silently.
> 
> This is purely about relocating an already-approved rule to the one
> reference every caller loads; it isn't a new behavior request.
