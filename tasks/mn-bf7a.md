+++
id = "mn-bf7a"
title = "daily-plan: fill the Time Block with meetings first, mark tentative ones, ask about overlaps"
kind = "feature"
state = "integrated"
created_at = "2026-09-28T23:49:27.404Z"
updated_at = "2026-09-29T01:48:36.281766Z"
+++

The human wants this in the plugin; their write-up follows verbatim. It changes skills/daily-plan/SKILL.md (a product skill shipped by the plugin) and, if it describes the skill, the matching spec (openspec/specs/ceremony-skills or similar).

Decisions (orchestrator; the human may override): do all four points. no-reply and null read the same as maybe, so all get the "(opt) " prefix; only yes is plain. Overlaps: ask the user, never drop silently. Keep the SKILL.md edits tight and in its existing style. Docs/skill-only change: no version bump unless the skill is versioned with the CLI (check .bridle/rules/versioning.md). Done = ./run_tests.sh && pipenv run pytest test/unit/ still green.

---

# project/meta-notes/daily-plan skill: fill Time Block from meetings by default

For the meta-notes plugin maintainer. This is a request to change the
shipped `daily-plan` SKILL.md (currently at
`skills/daily-plan/SKILL.md` in the plugin repo); nothing in this notes
repo should be edited to work around it.

## Problem

Step 5 of `daily-plan` ("Write the plan") currently says:

> Fill the Plan column of the `### Time Block` table: meetings at their
> times, then the most important work in the largest free blocks.

In practice, when asked to "plan my day," the assistant fetched
`meta-notes calendar --json`, summarized the meetings in prose, and
then stopped — it did not fill the Time Block table with them until
separately asked to. The instruction to place meetings in the table
exists, but doesn't say to do it immediately/first, doesn't say what to
write for a meeting whose `response` is `maybe`, and doesn't say
anything about overlapping events, so all three were left to
improvisation.

## Requested changes to `skills/daily-plan/SKILL.md`

### 1. Fill meetings into the Time Block immediately, before other work

Reorder/rewrite step 5 so filling in meetings happens as its own
sub-step, not lumped into "fill the whole Plan column at once" phrasing
that reads as optional-until-later. Suggested rewrite of step 5's first
point:

> 2. Fill the Plan column of the `### Time Block` table. First place
>    every meeting from step 3's agenda at its times — do this before
>    planning any other work in the table, even if the rest of the plan
>    isn't decided yet. Then fill the most important work into the
>    remaining free blocks. Edit only the Plan cells, keeping the
>    table's column widths.

### 2. Mark `maybe`/tentative meetings distinctly

`meta-notes calendar --json` already returns `response` per event
(`yes`, `maybe`, `no-reply`, or null — see the `calendar` skill's
SKILL.md, "Filtered output lists..."). `daily-plan` currently ignores
this field entirely when writing the Time Block. Add:

> When an event's `response` is `maybe`, `no-reply`, or null, write it
> with a leading `(opt) ` in the Plan cell, e.g. `(opt) mtg: DMDC
> Monthly Connect`, so tentative meetings are visually distinct from
> ones the user has accepted. Only `response: "yes"` meetings get plain
> text with no prefix.

(Whether `no-reply` should really read the same as `maybe` here is a
judgment call for the maintainer — a `no-reply` invite the user hasn't
acted on at all arguably deserves the same "not committed" treatment as
`maybe`, but it's worth deciding explicitly rather than leaving it
implicit.)

### 3. Ask the user about overlaps instead of silently dropping one

Two observed real events overlapped by 55 minutes (a `maybe` meeting
ending at 2:00pm partially overlapping a personal all-day-marked `OOO`
event starting at 2:00pm, plus a separate `maybe` meeting fully inside
the OOO window). The assistant picked one to keep and one to drop
without asking. Add a rule:

> Before filling overlapping events into the same time range, tell the
> user about the overlap and ask which to keep in the Plan cell (or
> whether to note both, e.g. `mtg: X / (opt) mtg: Y`). Don't silently
> drop one. Detect an overlap as two events whose `start`–`end` ranges
> intersect.

### 4. Small knock-on doc fix

The `calendar` skill's SKILL.md already documents the `response` field
and the `mine` field precisely (see its "Run" section: "`response` (the
user's: `yes`, `maybe`, `no-reply`, or null), `mine` (the user organized
it)"). `daily-plan`'s SKILL.md doesn't currently reference either field
by name even though step 3 already tells the assistant to pull
`days[0].events` — worth a one-line cross-reference so an implementer
doesn't have to go re-derive the field names from the other skill.

## Why this belongs in the plugin, not this repo

`daily-plan` is a symlinked skill
(`.claude/skills/daily-plan` → `~/.vim/bundle/meta-notes/skills/daily-plan`)
shipped by the meta-notes plugin, shared across notes roots. Any fix
belongs in the plugin's `SKILL.md` so every user of the plugin gets it,
not as a local override in this repo.

## Thread

### note · agent:manager · 2026-09-29T01:48:36.257Z
skills/daily-plan/SKILL.md step 5: meetings placed first; response maybe, no-reply or null get an (opt) prefix, only yes is plain; overlapping events are raised with the user, never dropped silently; cross-reference to the calendar skill's response and mine fields. ceremony-skills spec updated. Skill and spec only, no version bump.

### note · agent:manager · 2026-09-29T01:48:36.281Z
integrated: fcc53c1
