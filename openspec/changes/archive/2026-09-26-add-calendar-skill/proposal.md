## Why

`meta-notes calendar` gives agents the calendar as JSON, but only the
planning skills know it exists. Asked "do I have a 1-1 with Zach next
week?", "find any meetings with Loan Bui", or "find all meetings about
EFP", a fresh Claude session has no way to discover the command and asks
for a screenshot. Two gaps in the command make these questions unreliable
even once found: the JSON lists only the first 20 attendees of an event,
so a person in a large meeting can be missed, and event descriptions
aren't in the output, so a topic mentioned only there can't be found.

Depends on `add-calendar-export`, which adds `meta-notes calendar`; archive
that change first.

## What Changes

- **`calendar` skill.** A new `skills/calendar/SKILL.md`, linked into
  notes roots by `meta-notes init` like the other skills. Its description
  triggers on questions about the user's meetings (who, what, when, free
  time). It explains how to:
  - turn "next week", "Thursday", "this month" into a `--date` period,
    with a default when none is given
  - look for people and topics with the command's new filters, and read
    `attendees`, `organizer`, `attendee_count`, `response`, and `mine`
  - recognize a 1-1
  - report matches briefly, with the export's age and warnings, and fall
    back like `daily-plan` when the command fails
  - stay read-only
- **`meta-notes calendar --with NAME`** (repeatable) keeps only events
  where every NAME matches the organizer or an attendee, by name or
  email, checking all attendees, not just the first 20. Words match in
  any order and as prefixes, ignoring case: `Zach` matches
  `Zachary Kim`, and `Loan Bui` matches `bui.loan@example.com`.
- **`meta-notes calendar --search TEXT`** keeps only events whose title,
  location, or description contains TEXT, ignoring case.
- With either filter, each event in the JSON gains `matches`: the people
  that matched each `--with` name (even past the 20-attendee cap) and the
  fields that matched `--search`. Only days with a matching event are
  listed, so a month-long search stays short.
- The 20-attendee cap in unfiltered output stays, to keep a week's JSON
  small.

## Capabilities

### New Capabilities
- `calendar-skill`: the `calendar` skill: when it triggers, periods,
  people and topic lookups, 1-1s, reporting, fallbacks, read-only

### Modified Capabilities
- `calendar-agenda` (added by `add-calendar-export`): `--with` and
  `--search` filters and the `matches` field

## Impact

- `skills/calendar/SKILL.md`: new; `init` links it with no code change
- `scripts/meta_notes/calendar.py`, `scripts/meta_notes/cli.py`: filters
- `test/unit/test_calendar.py`, `test/unit/test_init.py`: filter tests,
  the shipped skill
- `doc/meta-notes.txt`, `README.md`: the options and the skill
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
