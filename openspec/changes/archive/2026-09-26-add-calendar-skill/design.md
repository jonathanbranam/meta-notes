## Context

See proposal.md for motivation. `meta-notes calendar` (from
`add-calendar-export`) builds each event's JSON in `calendar.agenda()`
from an expanded `icalendar` event, which still has every `ATTENDEE`,
the `ORGANIZER`, and the `DESCRIPTION`. `attendance()` already parses
attendees into people (rooms and resources dropped) before capping the
list at 20. The planning skills show the pattern a new skill follows:
check `meta-notes` is on `PATH`, run the command with `--json`, pass on
its warnings, and fall back to an export or a screenshot on failure.

## Goals / Non-Goals

**Goals:**
- A person or topic lookup is one command whose output holds only the
  answer, however large the meetings or long the period.
- The skill carries the judgment (periods, 1-1s, ambiguous names); the
  CLI does exact, testable matching.

**Non-Goals:**
- Free-time search as a CLI feature. The skill can work out gaps from an
  unfiltered agenda, as `weekly-plan` does.
- Fuzzy or phonetic name matching, nicknames (`Bob` for `Robert`), or a
  contacts lookup.
- Showing descriptions in the output. They're searched, not printed.

## Decisions

### 1. Filter in the CLI, keep the cap

Filtering happens in `agenda()`, per occurrence, against the full people
list and the event's description, before the cap and before the event
dict is built. Filtered output drops days without matches.

Alternatives:
- Remove the 20-attendee cap and let the skill search the JSON. A week of
  all-hands meetings becomes hundreds of KB, and an agent scanning JSON
  by eye misses names; exact matching is better done in code.
- Raise the cap. Moves the problem without fixing it.
- Add `description` to the JSON and let the skill search it. Same size
  problem; descriptions are often long HTML-ish text from Google.

### 2. Name matching by word starts

NAME and each person's name and email are split into words (runs of
letters and digits, lowercased). A person matches when every NAME word
is a prefix of some person word. So `zach` finds `Zachary`, `Loan Bui`
finds `bui.loan@...`, and `ann` doesn't find `Joanna`. The organizer is
checked as a person too (they may not be listed as an attendee).
`matches.with[].people` lists every matching person, with their
response when they're an attendee (null for an organizer-only match), so
the skill can spot two different Zachs.

Alternative: plain substring. `ann` would match `Joanna`, `joannak@`, and
`hannah`; too loose for names.

### 3. `--search` is a case-insensitive substring

Over title, location, and description, with no word splitting, so `1:1`,
`EFP`, and `Q3 planning` all work as typed. `matches.search[].fields`
names where it matched so the skill can explain a hit on a description.

### 4. Skill shape

`skills/calendar/SKILL.md` is short and procedural, like the planning
skills, but has no time budget and never runs `meta-notes conventions`
(it reads no notes). Sections: Start (PATH check), Period, Run (the
command forms), People, Topics, 1-1s, Answer, When the command fails.
The period rules and the 1-1 rule are the spec's; the skill states them
as instructions with the concrete command lines.

### 5. Output for filtered runs

Text: the same day headings and event lines as today, only for days with
matches; `No matching events.` when none. JSON: the same event objects
plus `matches`; `source`, `pruned`, and `warnings` unchanged.

## Risks / Trade-offs

- [Word-start matching misses nicknames and misspellings] → The skill
  retries with the first name and reports whom it matched; the user can
  rephrase.
- [A month-long `--search` expands every recurring series over 28 days]
  → Expansion already happens for the unfiltered agenda; it's the same
  work, and output is smaller.
- [Descriptions are searched but not shown, so a hit can look
  unrelated] → `matches.search[].fields` says it was the description.
