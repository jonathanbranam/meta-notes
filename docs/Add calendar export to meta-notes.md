# project/meta-notes/Add calendar export to meta-notes

## Background

`daily-plan` and `weekly-plan` currently ask for a screenshot of the
calendar and read it visually. That's slow, easy to get wrong (columns cut
off, day headers missing, ambiguous which week is shown), and can't be
automated. There's no Google Calendar API access available in this
environment, but Google Calendar can export a `.ics` file (Settings ->
Import & export -> Export) containing every calendar the account has, and
that file can be parsed into a plain-text agenda for a specific date
range that a skill can read directly instead of asking for a screenshot.

This note documents what was learned building and testing a prototype
parser against a real multi-year Google Calendar export, so the actual
implementation (which belongs in the meta-notes plugin, not this notes
repo) can skip re-discovering these issues.

The export used for testing was `jonathan.branam@capitalone.com`'s
calendar: a single `.ics` file, 38 MB, ~10,000 `VEVENT` blocks, covering
2022 through 2026, including thousands of recurring-meeting instances and
edit history. Real exports at this scale are slow to produce (Google
takes a while to generate the zip) and slow-ish to parse in full, so any
implementation should stream/filter rather than build up big in-memory
structures beyond what's needed for one date range.

## Libraries to use

Do **not** hand-roll RRULE expansion (a stdlib-only prototype was built
and tested for this, and it works, but reproduces a lot of the iCalendar
spec badly — see below). Use:

- [`icalendar`](https://pypi.org/project/icalendar/) — parses the `.ics`
  file into `Calendar`/`Event` objects, handles line unfolding, escaping,
  and property/parameter parsing correctly.
- [`recurring-ical-events`](https://pypi.org/project/recurring-ical-events/)
  — takes a parsed `icalendar.Calendar` and expands recurrence
  (`RRULE`/`RDATE`/`EXDATE`/`RECURRENCE-ID` overrides) for a given date
  range via `.between(start, end)`. This handled every recurrence pattern
  found in the real export (`DAILY`/`WEEKLY`/`MONTHLY`/`YEARLY`, `BYDAY`,
  `BYMONTHDAY`, `INTERVAL`, `COUNT`, `UNTIL`, `WKST`) with no bugs found
  in testing, unlike the hand-rolled version.

Both were confirmed already available in this repo's `.venv`
(`.venv/bin/python -c "import icalendar, recurring_ical_events"`
succeeds), so no new dependency approval should be needed if the meta-notes
plugin's Python environment is set up the same way.

## Basic usage

```python
import icalendar
import recurring_ical_events
from datetime import date, datetime

with open(ics_path, "rb") as f:
    cal = icalendar.Calendar.from_ical(f.read())

events = recurring_ical_events.of(cal).between(start_date, end_date)
```

Each returned `event` is an `icalendar.Event` (a dict-like object).
Useful properties:

- `event["DTSTART"].dt` — a `datetime` for timed events, or a plain
  `date` for all-day events. **Sorting a mixed list of events will raise
  `TypeError` if you compare a `date` to a `datetime` directly** — normalize
  both to `datetime` (e.g. midnight, naive) before sorting.
- `event["DTEND"].dt` — same shape as `DTSTART`; may be absent.
- `event.get("SUMMARY")`, `event.get("LOCATION")` — plain strings (already
  unescaped by `icalendar`).
- `event.get("STATUS")` — almost always `"CONFIRMED"` in real Google
  exports; `"CANCELLED"` was not observed in this data, but should still be
  filtered out defensively per the iCalendar spec.
- `event.get("ATTENDEE")` — a list of `vCalAddress` values (or a single
  value, not a list, if there's only one attendee — handle both shapes).
  Each has `.params` (a dict-like) with keys like `PARTSTAT`. To find your
  own response: iterate attendees, match on `"your-email@domain.com" in
  str(attendee)`, then read `attendee.params.get("PARTSTAT")`.

## Special handling required

### 1. Filter out declined events

Google Calendar's UI can still display events you've declined (this is
how one showed up in a real calendar screenshot during testing), but a
useful agenda for planning purposes should exclude them. Check the
attendee entry matching your own email for `PARTSTAT == "DECLINED"` and
skip those events. Whether to expose this as a flag (some users may want
declined events shown, e.g. to see what they're missing) is a product
decision, but the default should probably be to hide them since that
matches how the skills currently interpret a calendar screenshot (a
declined event isn't really "on the calendar" for planning purposes).

### 2. Filter out cancelled events

Skip any event where `STATUS == "CANCELLED"`, defensively, even though
this wasn't observed in the test export — Google can send cancellation
overrides (a `RECURRENCE-ID` override with `STATUS:CANCELLED`) for single
occurrences of an otherwise-recurring event, and those should not appear
in the agenda.

### 3. Watch for a stray-date leak from `recurring_ical_events`

In testing, a single call to `.between(date(2026, 9, 28), date(2026, 10,
2))` returned one event dated `2026-09-08` — outside the requested
window. This looked like it might be related to an all-day or multi-day
event whose expansion logic anchors on a different date than expected,
but the exact cause wasn't tracked down. **Before trusting the date range
from `.between()` blindly, filter the returned events' own `DTSTART`
date against the requested window as a final safety check** rather than
assuming the library's date filtering is exact.

### 4. Timezones

Real events in the test export used at least four different `TZID`
values in the same file (`America/New_York`, `America/Los_Angeles`,
`America/Chicago`, `America/Indiana/Indianapolis`), because meetings
organized by colleagues in other US time zones carry their organizer's
`VTIMEZONE` block. `icalendar` resolves these to proper timezone-aware
`datetime` objects already. When displaying times, convert every event's
`DTSTART`/`DTEND` to the user's own display timezone
(e.g. `dt.astimezone(ZoneInfo("America/New_York"))`) rather than assuming
the file's `X-WR-TIMEZONE` header applies to every event — individual
events can and do carry a different `TZID` than the calendar-level
default.

## Pitfalls found while hand-rolling RRULE expansion (do not repeat these)

These were discovered building a stdlib-only prototype before switching
to `recurring-ical-events`. They're recorded here as a warning against
re-implementing RRULE expansion by hand, and as background in case the
chosen library ever needs to be swapped out or debugged.

- **Google re-splits a recurring series into a new UID chain every time
  the series is edited.** A single logical recurring meeting can appear
  in the export as many different `UID`s over its lifetime (e.g.
  `abc123@google.com`, then `abc123_R20260302T190500@google.com` once
  edited starting from that date, then another `_R...` suffix at the next
  edit). Each chain has its own `RRULE` with its own `UNTIL`, meant to
  stop exactly where the next chain's `DTSTART` picks up. Any hand-rolled
  expansion has to treat each chain independently and must get the
  `UNTIL` boundary exactly right, or adjacent chains will produce a
  duplicate occurrence on the handoff date (this happened in testing:
  "CTML Weekly Forum" and "Fuel Station" both appeared twice on their
  transition dates before the bug below was fixed).
- **`UNTIL` is a UTC timestamp; comparing it as a naive date is wrong by
  one day near the boundary.** An `RRULE` like
  `UNTIL=20260924T035959Z` means "in UTC" — converted to
  `America/New_York`, that's `2026-09-23T23:59:59-04:00`, i.e. the series
  actually stops on 2026-09-23 local time, not 2026-09-24. Taking
  `.date()` on the raw UTC value directly (without converting to the
  event's local timezone first) caused exactly this off-by-one-day bug,
  which is what produced the duplicate occurrences mentioned above. This
  class of bug is exactly what `recurring-ical-events` handles correctly
  and is a good reason to prefer the library.
- **The same `UID`+`RECURRENCE-ID` pair can appear more than once in a
  single export**, apparently as snapshots from edit history (one
  recurring meeting's single occurrence appeared 13 times in the test
  file, all with the same `UID` and `RECURRENCE-ID` but different
  `SEQUENCE`/`LAST-MODIFIED`). A hand-rolled parser must deduplicate by
  keeping only the highest `(SEQUENCE, LAST-MODIFIED)` pair per
  `(UID, RECURRENCE-ID)` key. It's not clear whether `recurring-ical-events`
  does this deduplication internally or whether the raw `icalendar.Calendar`
  object still contains the duplicates before expansion — this should be
  checked when implementing, since if the library doesn't dedupe, the
  same fix would be needed on top of it.
- **`RECURRENCE-ID` overrides replace one occurrence's time and metadata,
  including possibly moving it to a different day than the master
  pattern would predict** (used for "move this one instance to a
  different time" edits). Any override must take precedence over what the
  base `RRULE` would generate for a matching date, keyed by
  `(UID, RECURRENCE-ID)`.
- Observed `RRULE` shapes worth having test coverage for, since they all
  appeared in real data: multiple `BYDAY` values in one rule (e.g.
  `BYDAY=MO,TU,WE,TH,FR`), `INTERVAL` values other than 1 (biweekly,
  every 3 or 4 or 6 weeks), `MONTHLY` with `BYDAY=-1TU` (last Tuesday of
  the month) and with `BYMONTHDAY`, `COUNT`-limited series, and `EXDATE`
  (single dates excluded from an otherwise-recurring series, distinct
  from a `RECURRENCE-ID` override).

## Suggested integration shape

1. A small script/module (e.g. `calendar_agenda.py`) that takes an `.ics`
   path, a start date, an end date, and the user's own email, and prints
   (or returns) a day-by-day plain-text agenda: one `## YYYY-MM-DD Www`
   heading per day in range, then each event as either `all day  Title`
   or `HH:MM-HH:MM  Title [Location]`, sorted chronologically, with
   declined/cancelled events excluded per above.
2. `daily-plan` and `weekly-plan` should read this output instead of
   asking for a calendar screenshot, once a recent-enough `.ics` export is
   available. Since the export is a manual, occasionally-slow step (not a
   live sync), the skill should tell the user how stale the export is
   (e.g. compare the file's mtime or an internal `DTSTAMP` to today) and
   prompt for a fresh export if it looks too old, rather than silently
   planning off outdated data.
3. Where the `.ics` file should live and how it's refreshed is an open
   question for the meta-notes plugin design (fixed path the skill always
   checks vs. asking for a path each time) — not decided here.
