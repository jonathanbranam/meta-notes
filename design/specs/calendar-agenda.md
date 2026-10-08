# calendar-agenda Specification

## Purpose
Specifies `meta-notes calendar`, which turns the user's latest Google Calendar export (a `.zip` or `.ics` file) into a day-by-day agenda for a period, and the export cache behind it, so planning skills can read meetings without a screenshot.

## Requirements

### Requirement: Calendar command  {#r-f91b}
The CLI SHALL provide `meta-notes calendar [--date PERIOD] [--ics PATH] [--json]`, which prints the agenda for PERIOD. PERIOD SHALL use the shared `--date` syntax and default to today. The command SHALL resolve the notes root like the other commands.

#### Scenario: Default period  {#s-5748}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes calendar` on 2026-09-28 with a current export
- **THEN** the agenda SHALL cover 2026-09-28 only

#### Scenario: Week range  {#s-be44}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes calendar --date 2026-09-28..2026-10-02`
- **THEN** the agenda SHALL have one day for each date from 2026-09-28 to 2026-10-02

### Requirement: Calendar settings  {#r-8cf2}
The command SHALL read these settings from the `[calendar]` table in `.meta-notes`:
- `email`: the user's address, used to leave out events they declined. When unset, no event SHALL be left out as declined, and the command SHALL warn that `email` is not set.
- `timezone`: an IANA timezone name in which times are shown and days are divided. When unset, the system's local timezone SHALL be used. An unknown name SHALL be an error.
- `stale_days`: a whole number of days after which an export is stale. When unset, 3.
- `calendars`: a list of calendar names to load from a zip export. When unset, all.
- `downloads` and `downloads_pattern`: a folder outside the notes root (`~` expanded) and a glob for the exports in it. Both are optional; see "Downloads pickup".

#### Scenario: Timezone conversion  {#s-c08c}
*Verification*: **non-executable**
- **WHEN** `timezone` is `America/New_York` and an event starts at 10:00 `America/Chicago`
- **THEN** the event SHALL be shown starting at 11:00

#### Scenario: Email unset  {#s-aaca}
*Verification*: **non-executable**
- **WHEN** `[calendar]` has no `email` and an event has the user as a declined attendee
- **THEN** the event SHALL be listed and the output SHALL include a warning that `email` is not set

### Requirement: Export discovery  {#r-fa3d}
With `--ics PATH`, the command SHALL read that file. Otherwise it SHALL read the newest file, by modification time, whose name ends in `.ics` or `.zip` directly inside `<root>/.meta-notes-cache/ics/`. The export's age SHALL be measured from its modification time.

#### Scenario: Newest export wins  {#s-4937}
*Verification*: **non-executable**
- **WHEN** `ics/` holds `a.zip` modified on 2026-09-24 and `b.ics` modified on 2026-09-25
- **THEN** the agenda SHALL come from `b.ics`

#### Scenario: Explicit path  {#s-c3d6}
*Verification*: **non-executable**
- **WHEN** the user passes `--ics ~/Downloads/export.zip`
- **THEN** the agenda SHALL come from that file, whatever `ics/` holds

#### Scenario: Other files ignored  {#s-ac65}
*Verification*: **non-executable**
- **WHEN** `ics/` holds only `notes.txt` and a folder `old/` containing `c.ics`
- **THEN** the command SHALL behave as if `ics/` held no export

### Requirement: No export available  {#r-1ed1}
When no export is found and no cached calendar exists, the command SHALL exit non-zero with an error that gives the absolute path of `.meta-notes-cache/ics/` and says to export from Google Calendar into it. When no export is found but a cached calendar exists, the command SHALL use the newest cached calendar and SHALL warn that the export it was built from is missing.

#### Scenario: Nothing at all  {#s-cb96}
*Verification*: **non-executable**
- **WHEN** `ics/` is empty and `calendar/` is empty
- **THEN** the command SHALL fail with an error naming the absolute path of `ics/`

#### Scenario: Export deleted after caching  {#s-531e}
*Verification*: **non-executable**
- **WHEN** the only export was cached and then deleted from `ics/`
- **THEN** the command SHALL print the agenda from the cached calendar with a warning that its export is missing

### Requirement: Zip exports  {#r-3ba7}
A `.zip` export SHALL be read without extracting it to disk. Each `.ics` member SHALL be one calendar, named by its `X-WR-CALNAME` property, or by its file name without `.ics` when that property is missing. When `calendars` is set, only calendars whose name or member file name without `.ics` matches an entry, ignoring case, SHALL be loaded; an entry that matches no calendar SHALL be an error listing the available names. When `calendars` is unset, all calendars SHALL be loaded. For a `.ics` export, the file SHALL be the one calendar and `calendars` SHALL NOT apply.

#### Scenario: Selected calendar  {#s-dcd2}
*Verification*: **non-executable**
- **WHEN** the zip holds calendars named `me@example.com`, `Holidays in United States`, and `Birthdays`, and `calendars = ["me@example.com"]`
- **THEN** only events from `me@example.com` SHALL appear

#### Scenario: Unknown calendar name  {#s-f7dd}
*Verification*: **non-executable**
- **WHEN** `calendars = ["work"]` and no calendar in the zip is named `work`
- **THEN** the command SHALL fail with an error listing `me@example.com`, `Holidays in United States`, and `Birthdays`

#### Scenario: All calendars  {#s-7ed9}
*Verification*: **non-executable**
- **WHEN** `calendars` is unset and the zip holds three calendars
- **THEN** events from all three SHALL appear, and the JSON output SHALL list all three as available and loaded

### Requirement: Events in the agenda  {#r-8c48}
The agenda SHALL include every occurrence of every event, including each occurrence of a recurring event, that overlaps a day in PERIOD in the display timezone, and no other. It SHALL apply recurrence rules, excluded dates, and changes to single occurrences as the export records them. It SHALL leave out:
- events with status `CANCELLED`
- events where the attendee whose address matches `email`, ignoring case, has declined
- earlier versions of an occurrence the export records more than once, keeping only the latest

A timed event SHALL appear on the day it starts. An all-day event SHALL appear on each day it covers within PERIOD. Within a day, all-day events SHALL come first, then timed events by start time.

#### Scenario: Declined meeting hidden  {#s-51a3}
*Verification*: **non-executable**
- **WHEN** `email = "me@example.com"` and an event lists `me@example.com` as an attendee with `PARTSTAT=DECLINED`
- **THEN** the event SHALL NOT appear

#### Scenario: Moved occurrence  {#s-1ed7}
*Verification*: **non-executable**
- **WHEN** a weekly Tuesday meeting has its 2026-09-29 occurrence moved to Wednesday 2026-09-30
- **THEN** the agenda SHALL show it on 2026-09-30 and not on 2026-09-29

#### Scenario: Series split at an edit  {#s-21c5}
*Verification*: **non-executable**
- **WHEN** a weekly meeting's series ends with `UNTIL=20260924T035959Z` and continues as a new series starting 2026-09-24 (`America/New_York`)
- **THEN** the agenda for 2026-09-24 SHALL show that meeting once

#### Scenario: Occurrence recorded twice  {#s-90cd}
*Verification*: **non-executable**
- **WHEN** the export holds the same occurrence of a meeting twice, at `SEQUENCE` 1 titled `Sync` and `SEQUENCE` 2 titled `Sync (moved)`
- **THEN** the agenda SHALL show `Sync (moved)` once

#### Scenario: Multi-day all-day event  {#s-d2e9}
*Verification*: **non-executable**
- **WHEN** an all-day event covers 2026-09-28 through 2026-09-30 and PERIOD is 2026-09-29..2026-10-02
- **THEN** it SHALL appear on 2026-09-29 and 2026-09-30

### Requirement: Agenda output  {#r-4ec6}
Without `--json`, the command SHALL print, for each day in PERIOD including days with no events, a heading `## YYYY-MM-DD Www`, then one line per event: `all day` or `HH:MM-HH:MM` in 24-hour time, two spaces, the title, then ` [maybe]` or ` [no-reply]` when that is the user's response to an event they didn't organize (see "Attendance"). The text SHALL NOT include locations, other attendees, accepted responses, or whether the event is the user's own. When more than one calendar is loaded, each event line SHALL end with ` (<calendar name>)`. Warnings SHALL go to stderr.

With `--json`, the object SHALL have `ok`, `days` (each with `date` and `events`, each event with `start`, `end`, `all_day`, `title`, `location`, `calendar`, `mine`, `organizer`, `response`, `attendee_count`, and `attendees`), `source` (the export's path, its modification time, its age in days, whether a cached calendar was used, and the available and loaded calendar names), `pruned` (paths deleted by pruning), and `warnings`.

#### Scenario: Text output  {#s-0d8e}
*Verification*: **non-executable**
- **WHEN** 2026-09-28 has an all-day event `Holiday` and a meeting `Standup` from 09:00 to 09:30 in `Room 4` that the user accepted, and one calendar is loaded
- **THEN** the output SHALL include `## 2026-09-28 Mon`, then `all day  Holiday`, then `09:00-09:30  Standup`

#### Scenario: Empty day  {#s-8c6a}
*Verification*: **non-executable**
- **WHEN** 2026-09-29 has no events and is in PERIOD
- **THEN** the output SHALL include the heading `## 2026-09-29 Tue` with no event lines after it

### Requirement: Attendance  {#r-e211}
Each event SHALL report, in the JSON output:
- `organizer`: the organizer's `name` (its `CN`, or null) and `email`, or null when the event has no organizer
- `mine`: true when the organizer's address matches `email`, ignoring case, or when the event has no organizer and no attendees (whatever its calendar is named); false otherwise. Every loaded calendar, that is every one in `calendars` (or all, when unset), is treated as the user's own; there is no owned/viewed distinction
- `response`: the user's own response, from the attendee whose address matches `email`: `yes` (`ACCEPTED`), `maybe` (`TENTATIVE`), or `no-reply` (`NEEDS-ACTION`); null when the user isn't an attendee, the response is missing or another value, or `email` is unset
- `attendee_count`: the number of attendees who are people, leaving out rooms and resources (`CUTYPE` `ROOM` or `RESOURCE`)
- `attendees`: the first 20 of those attendees in export order, each with `name`, `email`, and `response` (`yes`, `maybe`, `no-reply`, `no` for `DECLINED`, or null when missing or another value)

The text output SHALL show ` [maybe]` or ` [no-reply]` when `response` is `maybe` or `no-reply` and `mine` is false, and nothing otherwise.

#### Scenario: Maybe  {#s-2fa4}
*Verification*: **non-executable**
- **WHEN** the user's attendee entry has `PARTSTAT=TENTATIVE`
- **THEN** the event's `response` SHALL be `maybe` and its text line SHALL end with ` [maybe]`

#### Scenario: No reply  {#s-b121}
*Verification*: **non-executable**
- **WHEN** the user's attendee entry has `PARTSTAT=NEEDS-ACTION`
- **THEN** the event's `response` SHALL be `no-reply` and its text line SHALL end with ` [no-reply]`

#### Scenario: Created by the user  {#s-aa05}
*Verification*: **non-executable**
- **WHEN** the event's `ORGANIZER` is `mailto:me@example.com` and `email = "me@example.com"`
- **THEN** `mine` SHALL be true and the text line SHALL have no bracket

#### Scenario: Personal event without attendees  {#s-fa12}
*Verification*: **non-executable**
- **WHEN** an event in the calendar named `WORK` has no organizer and no attendees, and `email = "me@example.com"`
- **THEN** `mine` SHALL be true, `response` null, and `attendee_count` 0

#### Scenario: Large meeting  {#s-ef97}
*Verification*: **non-executable**
- **WHEN** an event has 30 people and a room as attendees
- **THEN** `attendee_count` SHALL be 30 and `attendees` SHALL list the first 20 people with their responses

### Requirement: Downloads pickup  {#r-1b0f}
When `downloads` and `downloads_pattern` are both set, each run SHALL first move (not copy) every file in the `downloads` folder matching the glob into `<root>/.meta-notes-cache/ics/`, keeping its extension and its modification time, and naming it for that modification time to the minute as `YYYY-MM-DD_HHMM`. When that name is taken it SHALL add seconds, then `-N`, and SHALL NOT overwrite. A missing folder or a failed move SHALL warn, and the command SHALL still run from the cache. The command SHALL NOT watch the folder outside a run.

#### Scenario: Matching file  {#s-7ffa}
*Verification*: **non-executable**
- **WHEN** `downloads_pattern = "Google*.zip"` and the folder holds `Google Calendar.zip` and `other.zip`
- **THEN** `Google Calendar.zip` SHALL be moved to `ics/` as a timestamped name, and `other.zip` SHALL stay

#### Scenario: Missing folder  {#s-4f05}
*Verification*: **non-executable**
- **WHEN** `downloads` names a folder that does not exist
- **THEN** the output SHALL include a warning and the agenda SHALL come from the cache

### Requirement: Stale export warning  {#r-39d6}
When the export used is older than `stale_days` days, the command SHALL succeed and SHALL warn with the export's age in days. The same SHALL apply to a cached calendar used without its export, using the export's recorded modification time.

#### Scenario: Default threshold  {#s-5b10}
*Verification*: **non-executable**
- **WHEN** `stale_days` is unset and the newest export was modified 4 days ago
- **THEN** the agenda SHALL print with a warning that the export is 4 days old

#### Scenario: Configured threshold  {#s-b265}
*Verification*: **non-executable**
- **WHEN** `stale_days = 7` and the newest export was modified 4 days ago
- **THEN** no stale warning SHALL be given

### Requirement: Export cache  {#r-5da0}
The command SHALL store what it reads from an export in `<root>/.meta-notes-cache/calendar/`, keyed by the export's file name, size, modification time, and the loaded calendar names, and SHALL reuse it while all four are unchanged. The agenda from a cached calendar SHALL equal the agenda from the export for any PERIOD that starts no more than 30 days before the cache was built. For a PERIOD that starts earlier, the command SHALL read the export directly when it exists, and otherwise SHALL use the cached calendar and warn that events before the cache's start may be missing. The command SHALL create `calendar/` when it is missing.

#### Scenario: Reuse  {#s-94c8}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes calendar` twice without changing the export or config
- **THEN** the second run's JSON SHALL report that a cached calendar was used, and both agendas SHALL be equal

#### Scenario: New export  {#s-b56b}
*Verification*: **non-executable**
- **WHEN** a new export is saved into `ics/` after a run
- **THEN** the next run SHALL read the new export and cache it

#### Scenario: Calendar selection changed  {#s-012b}
*Verification*: **non-executable**
- **WHEN** `calendars` changes between runs with the same export
- **THEN** the next run SHALL read the export again and cache it with the new selection

### Requirement: Pruning  {#r-2059}
Each `calendar` run SHALL, after choosing its source:
- delete every export in `ics/` except the 5 newest by modification time
- delete every cached calendar except those built from a kept export with the current `calendars` setting, and the one used by this run
- when `ics/` holds no export, delete every cached calendar except the newest

Pruning SHALL only delete files directly inside `ics/` whose names end in `.ics` or `.zip`, and files inside `calendar/`. Every deleted path SHALL be reported: in `pruned` with `--json`, on stderr without it.

#### Scenario: Old exports removed  {#s-8041}
*Verification*: **non-executable**
- **WHEN** `ics/` holds 7 exports
- **THEN** after the run it SHALL hold the 5 newest, and cached calendars built from the 2 deleted exports SHALL be deleted

#### Scenario: Other files kept  {#s-c975}
*Verification*: **non-executable**
- **WHEN** `ics/` holds 7 exports and `notes.txt`
- **THEN** `notes.txt` SHALL still exist after the run

### Requirement: Calendar dependencies missing  {#r-4a02}
When the libraries the calendar command needs are not installed for the interpreter running it, `meta-notes calendar` SHALL exit non-zero with an error that says calendar support is not installed in this notes root and to run `meta-notes init`, or `meta-notes init --force` when `.venv` exists. Other commands SHALL NOT need these libraries.

#### Scenario: No virtualenv  {#s-5097}
*Verification*: **non-executable**
- **WHEN** the notes root has no `.venv` and the system `python3` lacks the libraries
- **THEN** `meta-notes calendar` SHALL fail with the not-installed error, and `meta-notes tasks` SHALL work

### Requirement: Cache clear command  {#r-e9f3}
The CLI SHALL provide `meta-notes cache clear [--json]`, which deletes every file in `<root>/.meta-notes-cache/calendar/` and reports how many it deleted. It SHALL NOT delete anything in `ics/` or `.meta-notes-cache/README.md`, and a missing `calendar/` SHALL NOT be an error. It SHALL NOT need the calendar libraries.

#### Scenario: Clear  {#s-1d2a}
*Verification*: **non-executable**
- **WHEN** `calendar/` holds 2 cached calendars and `ics/` holds 3 exports
- **THEN** after `meta-notes cache clear`, `calendar/` SHALL be empty, `ics/` SHALL hold the 3 exports, and the report SHALL say 2 were deleted

#### Scenario: Nothing to clear  {#s-cf7c}
*Verification*: **non-executable**
- **WHEN** `.meta-notes-cache/calendar/` does not exist
- **THEN** `meta-notes cache clear` SHALL succeed and report 0 deleted

### Requirement: People filter  {#r-aeb0}
`meta-notes calendar` SHALL accept `--with NAME`, repeatable. A person SHALL match NAME when every word of NAME, ignoring case, is the start of a word in the person's name or email address, in any order; words are runs of letters and digits. An event SHALL match NAME when its organizer or any of its attendees who are people matches, checking every attendee, not only those listed in `attendees`. With `--with`, only events that match every NAME SHALL be included. A NAME without letters or digits SHALL be an error.

#### Scenario: First name as a prefix  {#s-3ae8}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes calendar --with zach` and an event has the attendee `Zachary Kim <zkim@example.com>`
- **THEN** the event SHALL be included

#### Scenario: Name found in the email address  {#s-9a09}
*Verification*: **non-executable**
- **WHEN** the user runs `--with "Loan Bui"` and an attendee has no name and the address `bui.loan@example.com`
- **THEN** the event SHALL be included

#### Scenario: Attendee past the list cap  {#s-7937}
*Verification*: **non-executable**
- **WHEN** the user runs `--with sapna` and Sapna is the 25th of 30 attendees
- **THEN** the event SHALL be included, and its `matches` SHALL list Sapna

#### Scenario: Two names  {#s-bd6a}
*Verification*: **non-executable**
- **WHEN** the user runs `--with zach --with sapna` and an event has Zach but not Sapna
- **THEN** the event SHALL NOT be included

#### Scenario: Word start only  {#s-2f68}
*Verification*: **non-executable**
- **WHEN** the user runs `--with ann` and the only attendee is `Joanna Smith <jsmith@example.com>`
- **THEN** the event SHALL NOT be included

### Requirement: Text search  {#r-1736}
`meta-notes calendar` SHALL accept `--search TEXT`, repeatable. An event SHALL match TEXT when its title, location, or description contains TEXT, ignoring case. With `--search`, only events that match every TEXT SHALL be included.

#### Scenario: Topic in the description  {#s-724b}
*Verification*: **non-executable**
- **WHEN** the user runs `--search efp` and an event titled `Quarterly sync` has `EFP rollout` in its description
- **THEN** the event SHALL be included, with `description` as the matching field

#### Scenario: Filters combined  {#s-b278}
*Verification*: **non-executable**
- **WHEN** the user runs `--with zach --search 1:1`
- **THEN** only events that match both SHALL be included

### Requirement: Filtered output  {#r-decc}
With `--with` or `--search`, the text and JSON output SHALL include only the days in PERIOD that have a matching event, in date order, each with only its matching events. When no event matches, the command SHALL succeed; the text output SHALL be the line `No matching events.` and the JSON `days` SHALL be empty. In the JSON, each included event SHALL have `matches`, an object with `with`, a list with one entry per `--with` NAME (`name`, and `people`: every organizer or attendee that matched, each with `name`, `email`, and `response`), and `search`, a list with one entry per `--search` TEXT (`text`, and `fields`: the matching fields among `title`, `location`, and `description`). Without a filter, the output SHALL be unchanged, and events SHALL NOT have `matches`.

#### Scenario: Only matching days  {#s-83f9}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes calendar --date 2026-09-28..2026-10-02 --with zach` and Zach is only in a meeting on 2026-09-30
- **THEN** the output SHALL have only the day 2026-09-30, with only that meeting

#### Scenario: No matches  {#s-97f2}
*Verification*: **non-executable**
- **WHEN** no event in PERIOD matches `--with nobody`
- **THEN** the command SHALL exit 0, print `No matching events.`, and with `--json` return an empty `days`

#### Scenario: Matches in JSON  {#s-9501}
*Verification*: **non-executable**
- **WHEN** the user runs `--with zach --json` and Zachary Kim accepted the meeting
- **THEN** the event's `matches.with` SHALL be `[{"name": "zach", "people": [{"name": "Zachary Kim", "email": "zkim@example.com", "response": "yes"}]}]`
