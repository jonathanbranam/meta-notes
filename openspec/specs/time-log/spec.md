## Purpose

Specifies how time log entries in daily notes record when an activity started and ended: which timestamp formats a `start:` or `end:` line accepts, how a bare time gets its date, and how the shipped daily template and syntax highlighting present those timestamps.

## Requirements

### Requirement: Time log timestamps accept four formats
A `start:` or `end:` line in a time log entry SHALL accept a timestamp in any of these formats:

| Format | Example | Date comes from |
|---|---|---|
| Bare 24-hour time | `09:10`, `9:10` | Note filename |
| Bare 12-hour time | `3:20pm`, `3:20 pm` | Note filename |
| Full date without day abbreviation | `2026-02-14 08:00` | The timestamp |
| Full date with day abbreviation | `2026-02-14 Sat 08:00` | The timestamp |

Leading and trailing whitespace around the timestamp SHALL be ignored.

#### Scenario: Bare 24-hour time
- **WHEN** the note `plan/daily/26-Q1/2026-02-14 Sat.md` contains `* start: 09:10`
- **THEN** the entry's start time SHALL be 2026-02-14 09:10

#### Scenario: Bare 12-hour time
- **WHEN** the note `plan/daily/26-Q1/2026-02-14 Sat.md` contains `* start: 3:20pm`
- **THEN** the entry's start time SHALL be 2026-02-14 15:20

#### Scenario: Full date without day abbreviation
- **WHEN** a time log contains `* start: 2026-02-14 08:00`
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

#### Scenario: Full date with day abbreviation
- **WHEN** a time log contains `* start: 2026-02-14 Sat 08:00`
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

#### Scenario: Extra spacing after the field name
- **WHEN** a time log contains `* end:   10:00` in the note `2026-02-14 Sat.md`
- **THEN** the entry's end time SHALL be 2026-02-14 10:00

### Requirement: A full date's own date takes precedence over the filename
A timestamp that includes a date SHALL use that date, even when the note's filename contains a different date. The day abbreviation, when present, SHALL NOT be checked against the date.

#### Scenario: Full date in a note for another day
- **WHEN** the note `2026-02-14 Sat.md` contains `* end: 2026-02-15 01:30`
- **THEN** the entry's end time SHALL be 2026-02-15 01:30

#### Scenario: Mismatched day abbreviation
- **WHEN** a time log contains `* start: 2026-02-14 Mon 08:00` (2026-02-14 is a Saturday)
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

### Requirement: Formats may be mixed within a note
Each `start:` and `end:` value SHALL be parsed independently, so one note, and one entry, MAY use different formats.

#### Scenario: Mixed formats in one log
- **WHEN** the note `2026-02-14 Sat.md` has one entry with `* start: 2026-02-14 Sat 08:00` and `* end: 09:00`, and a second entry with `* start: 09:00` and `* end: 2026-02-14 10:15`
- **THEN** the first entry SHALL run from 2026-02-14 08:00 to 09:00
- **AND** the second entry SHALL run from 2026-02-14 09:00 to 10:15

### Requirement: Unparseable timestamps leave the time unset
A `start:` or `end:` value that matches none of the accepted formats, or that names an invalid date or time, SHALL leave that time unset. The entry itself SHALL still be recorded. A bare time in a note whose filename contains no `YYYY-MM-DD` date SHALL be treated as unparseable.

#### Scenario: Placeholder left in the log
- **WHEN** a time log contains `* start: HH:MM`
- **THEN** the entry's start time SHALL be unset

#### Scenario: Out-of-range time
- **WHEN** a time log in the note `2026-02-14 Sat.md` contains `* start: 25:00`
- **THEN** the entry's start time SHALL be unset

#### Scenario: Bare time in a note without a date in its name
- **WHEN** the note `project/notes.md` contains a time log with `* start: 09:10`
- **THEN** the entry's start time SHALL be unset

### Requirement: Daily template pre-fills bare time placeholders
The shipped daily template SHALL pre-fill the time log's starter entry with bare time placeholders (`* start: HH:MM` and `* end:   HH:MM`), with no date.

#### Scenario: New daily note
- **WHEN** a daily note for 2026-09-25 is created from the shipped daily template
- **THEN** its time log starter entry SHALL contain `* start: HH:MM` and `* end:   HH:MM`
- **AND** SHALL NOT contain `2026-09-25` on those lines

### Requirement: Time log timestamps are highlighted
In markdown buffers, the time part of a `start:` or `end:` timestamp SHALL be highlighted as a time in every accepted format, both 24-hour and 12-hour.

#### Scenario: 24-hour time highlighted
- **WHEN** a markdown buffer contains `  * start: 09:10`
- **THEN** `09:10` SHALL be highlighted as a time

#### Scenario: 12-hour time highlighted
- **WHEN** a markdown buffer contains `  * start: 3:20pm`
- **THEN** `3:20pm` SHALL be highlighted as a time

#### Scenario: Time in a full-date timestamp highlighted
- **WHEN** a markdown buffer contains `  * end:   2026-02-14 Sat 09:00`
- **THEN** `09:00` SHALL be highlighted as a time
