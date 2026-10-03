---
id: zqqb
title: "time-block skill: how to edit the Time Block, with the human's style"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [kkrj, u34c, zyab]
tasks: [mn-49a5]
---

# time-block skill: how to edit the Time Block, with the human's style

The human, 2026-10-03 (relayed by the notes advisor), wants a skill rather
than startup instructions, partly to try skills out: "whether this is in
startup instructions or a skill is a little bit moot since you'll be doing
this every single day. But I think just for the purposes of experimenting
with our system, I kind of want to see it as a skill." When an agent is
asked to adjust the Time Block, the skill gives it:

- how `time-block update`, `time-block replace` (kkrj, v2.12.0) and
  `checkin actual` work, and when to use each;
- the standard prefixes: `mtg:` and the others;
- style: lowercase almost always ("I very rarely want to see uppercase");
- how tags work in cells, and the common tags;
- what `[square brackets]`, `(parens)` and `~tildes~` mean in a cell;
- no Markdown emphasis in the table (Vim conceal breaks alignment).

Shipped in `skills/time-block/`, linked by `init` like the others, and
starting from `meta-notes conventions`.

## Needs the human

Only some of the notation is written down. The highlighting
(`after/syntax/markdown.vim`, `:help meta-notes-timeblock-hl`) knows
`mtg:`, `train:`, `pers:`, `work:`, `[brackets]`, `(parens)` and `~text~`,
but not what they mean. `~text~` is off plan (struck through), and
`daily-plan` writes `(opt) ` for an optional meeting. The human's work notes
have examples. Before this is ready, they confirm the meaning of each
marker, any other prefixes, and the common tags.

Also decide which parts are the human's own rather than meta-notes'. The
generic part (CLI use, the markers meta-notes highlights, no emphasis in
tables) belongs in the shipped skill. Personal abbreviations and tags may
belong in the notes root's `CLAUDE.md`, which the skill tells the agent to
read; zyab (personal vs work) bears on this. Until then the notes root's
`CLAUDE.md` holds `mtg:` and the no-emphasis rule as a stopgap; move them
here when the skill exists.

The human also expects bridle to provide skills to a project through its
rules overlay eventually (not built); that's a bridle question, sent to
dalek. This skill ships with meta-notes either way.

## More from the human, 2026-10-03

- Time blocking is Cal Newport's. On paper they kept two Plan columns (the
  morning plan, then a replan) plus Actual. Actual stays blank when they
  did what was planned; it records deviations and extras. One Plan column,
  rewritten when replanning, is fine.
- Text in the Time Block and Time Log starts lowercase except proper names
  ("we're not writing real sentences here").
- These are in the notes root's `CLAUDE.md` for now.

## Tildes: off-plan rows (the human, 2026-10-03)

> If my actual is different than my planned... you don't change the plan
> because it's already happened. What you do is you surround the plan with
> tildes... and then left there... it shows that, like, I made a plan, and
> then I just did something else completely. And then the actual should be
> kind of a short summary of what actually happened. And then the time log
> records exactly what happened

The Time Log is the "literal truth", to the minute; Actual is a short
summary; only future rows get replanned.

Single or double tildes is the human's to confirm. The plugin today uses
single: `:help meta-notes-timeblock-hl` documents `~text~`, and
`after/syntax/markdown.vim` (`metaNotesOffPlan`) strikes `~text~` through.
That pattern also matches inside `~~text~~`, which Obsidian renders as
strikethrough and single tildes don't. The notes advisor wrote `~~text~~`
meanwhile.

Possible CLI support, part of this ticket or its own: `time-block update
--strike` wraps the existing Plan text in the agreed tildes (with the usual
`--expect`), so the agent doesn't retype it.

## Scope for today (2026-10-03)

The human asked for it today if the workforce can ("this needs to be built
into Bridle. So as rules or skills... If you can do that today, do it
today"). Bridle can't deliver skills to a project yet, so it ships the way
meta-notes' skills already do: `skills/time-block/SKILL.md`, linked into a
notes root by `meta-notes init`. Source text: the notes root's `CLAUDE.md`,
sections "My day" and "Time log tags" (notes commit ab2e4d8), quoted above.

Build:

- **When**: the user asks to plan, replan, fix or fill the Time Block, or
  to record what they did instead.
- **Commands**: `time-block update` (one cell, or a range set to the same
  text, `--create` for a missing row), `time-block replace` (rewrite a
  range in one call), `checkin actual`, and `time-log append`/`update`
  for the log. Always read first, always pass `--expect`; never edit the
  table by hand.
- **Rules**: replan only rows that haven't happened; a past row whose plan
  didn't happen keeps its Plan wrapped in `~~ ~~` and gets a short Actual;
  Actual stays blank when the plan happened; the Time Log is the literal
  truth, to the minute; meetings start `mtg:` and aren't moved or replaced;
  lowercase except proper names; no Markdown emphasis in the table (tildes
  are the one exception).
- **Defaults until the human says otherwise**: double tildes, as in the
  notes root's `CLAUDE.md`; `[brackets]`, `(parens)` and other prefixes
  (`train:`, `pers:`, `work:`, `(opt)`) are kept as written and never
  invented; ask the user what they mean if it matters.
- **Personal parts** (tags, working hours, the workout block) stay in the
  notes root's `CLAUDE.md`; the skill tells the agent to follow it.
- `daily-plan` and `checkin` point to this skill for Time Block edits
  instead of repeating the rules; README's skill table and `prime`'s skill
  list name it.

Out for now: `--strike` (a follow-up if retyping the plan proves error
prone); changing the Vim highlighting or `:help` on tildes.

## Done means

The skill exists and passes whatever checks the other skills have (see
`test/unit/test_prime.py` or similar for skill lists); README, `prime` and
the two skills updated. PATCH bump (docs and skills only).
