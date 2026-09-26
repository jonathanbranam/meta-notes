## Purpose

Specifies `meta-notes calendar`, which turns the user's latest Google Calendar export (a `.zip` or `.ics` file) into a day-by-day agenda for a period, and the export cache behind it, so planning skills can read meetings without a screenshot.

## ADDED Requirements

### Requirement: Calendar command
The CLI SHALL provide `meta-notes calendar [--date PERIOD] [--ics PATH] [--json]`, which prints the agenda for PERIOD. PERIOD SHALL use the shared `--date` syntax and default to today. The command SHALL resolve the notes root like the other commands.

#### Scenario: Default period
- **WHEN** the user runs `meta-notes calendar` on 2026-09-28 with a current export
- **THEN** the agenda SHALL cover 2026-09-28 only

#### Scenario: Week range
- **WHEN** the user runs `meta-notes calendar --date 2026-09-28..2026-10-02`
- **THEN** the agenda SHALL have one day for each date from 2026-09-28 to 2026-10-02

### Requirement: Calendar settings
The command SHALL read these settings from the `[calendar]` table in `.meta-notes`:
- `email`: the user's address, used to leave out events they declined. When unset, no event SHALL be left out as declined, and the command SHALL warn that `email` is not set.
- `timezone`: an IANA timezone name in which times are shown and days are divided. When unset, the system's local timezone SHALL be used. An unknown name SHALL be an error.
- `stale_days`: a whole number of days after which an export is stale. When unset, 3.
- `calendars`: a list of calendar names to load from a zip export. When unset, all.

#### Scenario: Timezone conversion
- **WHEN** `timezone` is `America/New_York` and an event starts at 10:00 `America/Chicago`
- **THEN** the event SHALL be shown starting at 11:00

#### Scenario: Email unset
- **WHEN** `[calendar]` has no `email` and an event has the user as a declined attendee
- **THEN** the event SHALL be listed and the output SHALL include a warning that `email` is not set

### Requirement: Export discovery
With `--ics PATH`, the command SHALL read that file. Otherwise it SHALL read the newest file, by modification time, whose name ends in `.ics` or `.zip` directly inside `<root>/.meta-notes-cache/ics/`. The export's age SHALL be measured from its modification time.

#### Scenario: Newest export wins
- **WHEN** `ics/` holds `a.zip` modified on 2026-09-24 and `b.ics` modified on 2026-09-25
- **THEN** the agenda SHALL come from `b.ics`

#### Scenario: Explicit path
- **WHEN** the user passes `--ics ~/Downloads/export.zip`
- **THEN** the agenda SHALL come from that file, whatever `ics/` holds

#### Scenario: Other files ignored
- **WHEN** `ics/` holds only `notes.txt` and a folder `old/` containing `c.ics`
- **THEN** the command SHALL behave as if `ics/` held no export

### Requirement: No export available
When no export is found and no cached calendar exists, the command SHALL exit non-zero with an error that gives the absolute path of `.meta-notes-cache/ics/` and says to export from Google Calendar into it. When no export is found but a cached calendar exists, the command SHALL use the newest cached calendar and SHALL warn that the export it was built from is missing.

#### Scenario: Nothing at all
- **WHEN** `ics/` is empty and `calendar/` is empty
- **THEN** the command SHALL fail with an error naming the absolute path of `ics/`

#### Scenario: Export deleted after caching
- **WHEN** the only export was cached and then deleted from `ics/`
- **THEN** the command SHALL print the agenda from the cached calendar with a warning that its export is missing

### Requirement: Zip exports
A `.zip` export SHALL be read without extracting it to disk. Each `.ics` member SHALL be one calendar, named by its `X-WR-CALNAME` property, or by its file name without `.ics` when that property is missing. When `calendars` is set, only calendars whose name or member file name without `.ics` matches an entry, ignoring case, SHALL be loaded; an entry that matches no calendar SHALL be an error listing the available names. When `calendars` is unset, all calendars SHALL be loaded. For a `.ics` export, the file SHALL be the one calendar and `calendars` SHALL NOT apply.

#### Scenario: Selected calendar
- **WHEN** the zip holds calendars named `me@example.com`, `Holidays in United States`, and `Birthdays`, and `calendars = ["me@example.com"]`
- **THEN** only events from `me@example.com` SHALL appear

#### Scenario: Unknown calendar name
- **WHEN** `calendars = ["work"]` and no calendar in the zip is named `work`
- **THEN** the command SHALL fail with an error listing `me@example.com`, `Holidays in United States`, and `Birthdays`

#### Scenario: All calendars
- **WHEN** `calendars` is unset and the zip holds three calendars
- **THEN** events from all three SHALL appear, and the JSON output SHALL list all three as available and loaded

### Requirement: Events in the agenda
The agenda SHALL include every occurrence of every event, including each occurrence of a recurring event, that overlaps a day in PERIOD in the display timezone, and no other. It SHALL apply recurrence rules, excluded dates, and changes to single occurrences as the export records them. It SHALL leave out:
- events with status `CANCELLED`
- events where the attendee whose address matches `email`, ignoring case, has declined
- earlier versions of an occurrence the export records more than once, keeping only the latest

A timed event SHALL appear on the day it starts. An all-day event SHALL appear on each day it covers within PERIOD. Within a day, all-day events SHALL come first, then timed events by start time.

#### Scenario: Declined meeting hidden
- **WHEN** `email = "me@example.com"` and an event lists `me@example.com` as an attendee with `PARTSTAT=DECLINED`
- **THEN** the event SHALL NOT appear

#### Scenario: Moved occurrence
- **WHEN** a weekly Tuesday meeting has its 2026-09-29 occurrence moved to Wednesday 2026-09-30
- **THEN** the agenda SHALL show it on 2026-09-30 and not on 2026-09-29

#### Scenario: Series split at an edit
- **WHEN** a weekly meeting's series ends with `UNTIL=20260924T035959Z` and continues as a new series starting 2026-09-24 (`America/New_York`)
- **THEN** the agenda for 2026-09-24 SHALL show that meeting once

#### Scenario: Occurrence recorded twice
- **WHEN** the export holds the same occurrence of a meeting twice, at `SEQUENCE` 1 titled `Sync` and `SEQUENCE` 2 titled `Sync (moved)`
- **THEN** the agenda SHALL show `Sync (moved)` once

#### Scenario: Multi-day all-day event
- **WHEN** an all-day event covers 2026-09-28 through 2026-09-30 and PERIOD is 2026-09-29..2026-10-02
- **THEN** it SHALL appear on 2026-09-29 and 2026-09-30

### Requirement: Agenda output
Without `--json`, the command SHALL print, for each day in PERIOD including days with no events, a heading `## YYYY-MM-DD Www`, then one line per event: `all day` or `HH:MM-HH:MM` in 24-hour time, two spaces, the title, then ` [location]` when the event has a location. When more than one calendar is loaded, each event line SHALL end with ` (<calendar name>)`. Warnings SHALL go to stderr.

With `--json`, the object SHALL have `ok`, `days` (each with `date` and `events`, each event with `start`, `end`, `all_day`, `title`, `location`, and `calendar`), `source` (the export's path, its modification time, its age in days, whether a cached calendar was used, and the available and loaded calendar names), `pruned` (paths deleted by pruning), and `warnings`.

#### Scenario: Text output
- **WHEN** 2026-09-28 has an all-day event `Holiday` and a meeting `Standup` from 09:00 to 09:30 in `Room 4`, and one calendar is loaded
- **THEN** the output SHALL include `## 2026-09-28 Mon`, then `all day  Holiday`, then `09:00-09:30  Standup [Room 4]`

#### Scenario: Empty day
- **WHEN** 2026-09-29 has no events and is in PERIOD
- **THEN** the output SHALL include the heading `## 2026-09-29 Tue` with no event lines after it

### Requirement: Stale export warning
When the export used is older than `stale_days` days, the command SHALL succeed and SHALL warn with the export's age in days. The same SHALL apply to a cached calendar used without its export, using the export's recorded modification time.

#### Scenario: Default threshold
- **WHEN** `stale_days` is unset and the newest export was modified 4 days ago
- **THEN** the agenda SHALL print with a warning that the export is 4 days old

#### Scenario: Configured threshold
- **WHEN** `stale_days = 7` and the newest export was modified 4 days ago
- **THEN** no stale warning SHALL be given

### Requirement: Export cache
The command SHALL store what it reads from an export in `<root>/.meta-notes-cache/calendar/`, keyed by the export's file name, size, modification time, and the loaded calendar names, and SHALL reuse it while all four are unchanged. The agenda from a cached calendar SHALL equal the agenda from the export for any PERIOD that starts no more than 30 days before the cache was built. For a PERIOD that starts earlier, the command SHALL read the export directly when it exists, and otherwise SHALL use the cached calendar and warn that events before the cache's start may be missing. The command SHALL create `calendar/` when it is missing.

#### Scenario: Reuse
- **WHEN** the user runs `meta-notes calendar` twice without changing the export or config
- **THEN** the second run's JSON SHALL report that a cached calendar was used, and both agendas SHALL be equal

#### Scenario: New export
- **WHEN** a new export is saved into `ics/` after a run
- **THEN** the next run SHALL read the new export and cache it

#### Scenario: Calendar selection changed
- **WHEN** `calendars` changes between runs with the same export
- **THEN** the next run SHALL read the export again and cache it with the new selection

### Requirement: Pruning
Each `calendar` run SHALL, after choosing its source:
- delete every export in `ics/` except the 5 newest by modification time
- delete every cached calendar except those built from a kept export with the current `calendars` setting, and the one used by this run
- when `ics/` holds no export, delete every cached calendar except the newest

Pruning SHALL only delete files directly inside `ics/` whose names end in `.ics` or `.zip`, and files inside `calendar/`. Every deleted path SHALL be reported: in `pruned` with `--json`, on stderr without it.

#### Scenario: Old exports removed
- **WHEN** `ics/` holds 7 exports
- **THEN** after the run it SHALL hold the 5 newest, and cached calendars built from the 2 deleted exports SHALL be deleted

#### Scenario: Other files kept
- **WHEN** `ics/` holds 7 exports and `notes.txt`
- **THEN** `notes.txt` SHALL still exist after the run

### Requirement: Calendar dependencies missing
When the libraries the calendar command needs are not installed for the interpreter running it, `meta-notes calendar` SHALL exit non-zero with an error that says calendar support is not installed in this notes root and to run `meta-notes init`, or `meta-notes init --force` when `.venv` exists. Other commands SHALL NOT need these libraries.

#### Scenario: No virtualenv
- **WHEN** the notes root has no `.venv` and the system `python3` lacks the libraries
- **THEN** `meta-notes calendar` SHALL fail with the not-installed error, and `meta-notes tasks` SHALL work

### Requirement: Cache clear command
The CLI SHALL provide `meta-notes cache clear [--json]`, which deletes every file in `<root>/.meta-notes-cache/calendar/` and reports how many it deleted. It SHALL NOT delete anything in `ics/` or `.meta-notes-cache/README.md`, and a missing `calendar/` SHALL NOT be an error. It SHALL NOT need the calendar libraries.

#### Scenario: Clear
- **WHEN** `calendar/` holds 2 cached calendars and `ics/` holds 3 exports
- **THEN** after `meta-notes cache clear`, `calendar/` SHALL be empty, `ics/` SHALL hold the 3 exports, and the report SHALL say 2 were deleted

#### Scenario: Nothing to clear
- **WHEN** `.meta-notes-cache/calendar/` does not exist
- **THEN** `meta-notes cache clear` SHALL succeed and report 0 deleted
