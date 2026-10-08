## Purpose

Specifies how time log entries in daily notes record when an activity started and ended: which timestamp formats a `start:` or `end:` line accepts, how a bare time gets its date, and how the shipped daily template and syntax highlighting present those timestamps.

## Requirements

### Requirement: Time log timestamps accept four formats  {#r-2631}
A `start:` or `end:` line in a time log entry SHALL accept a timestamp in any of these formats:

| Format | Example | Date comes from |
|---|---|---|
| Bare 24-hour time | `09:10`, `9:10` | Note filename |
| Bare 12-hour time | `3:20pm`, `3:20 pm` | Note filename |
| Full date without day abbreviation | `2026-02-14 08:00` | The timestamp |
| Full date with day abbreviation | `2026-02-14 Sat 08:00` | The timestamp |

Leading and trailing whitespace around the timestamp SHALL be ignored.

#### Scenario: Bare 24-hour time  {#s-69ec}
*Verification*: **non-executable**
- **WHEN** the note `plan/daily/26-Q1/2026-02-14 Sat.md` contains `* start: 09:10`
- **THEN** the entry's start time SHALL be 2026-02-14 09:10

#### Scenario: Bare 12-hour time  {#s-ad82}
*Verification*: **non-executable**
- **WHEN** the note `plan/daily/26-Q1/2026-02-14 Sat.md` contains `* start: 3:20pm`
- **THEN** the entry's start time SHALL be 2026-02-14 15:20

#### Scenario: Full date without day abbreviation  {#s-2dbd}
*Verification*: **non-executable**
- **WHEN** a time log contains `* start: 2026-02-14 08:00`
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

#### Scenario: Full date with day abbreviation  {#s-38af}
*Verification*: **non-executable**
- **WHEN** a time log contains `* start: 2026-02-14 Sat 08:00`
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

#### Scenario: Extra spacing after the field name  {#s-aa3d}
*Verification*: **non-executable**
- **WHEN** a time log contains `* end:   10:00` in the note `2026-02-14 Sat.md`
- **THEN** the entry's end time SHALL be 2026-02-14 10:00

### Requirement: A full date's own date takes precedence over the filename  {#r-05b5}
A timestamp that includes a date SHALL use that date, even when the note's filename contains a different date. The day abbreviation, when present, SHALL NOT be checked against the date.

#### Scenario: Full date in a note for another day  {#s-cdf4}
*Verification*: **non-executable**
- **WHEN** the note `2026-02-14 Sat.md` contains `* end: 2026-02-15 01:30`
- **THEN** the entry's end time SHALL be 2026-02-15 01:30

#### Scenario: Mismatched day abbreviation  {#s-f195}
*Verification*: **non-executable**
- **WHEN** a time log contains `* start: 2026-02-14 Mon 08:00` (2026-02-14 is a Saturday)
- **THEN** the entry's start time SHALL be 2026-02-14 08:00

### Requirement: Formats may be mixed within a note  {#r-7b88}
Each `start:` and `end:` value SHALL be parsed independently, so one note, and one entry, MAY use different formats.

#### Scenario: Mixed formats in one log  {#s-a594}
*Verification*: **non-executable**
- **WHEN** the note `2026-02-14 Sat.md` has one entry with `* start: 2026-02-14 Sat 08:00` and `* end: 09:00`, and a second entry with `* start: 09:00` and `* end: 2026-02-14 10:15`
- **THEN** the first entry SHALL run from 2026-02-14 08:00 to 09:00
- **AND** the second entry SHALL run from 2026-02-14 09:00 to 10:15

### Requirement: Unparseable timestamps leave the time unset  {#r-6566}
A `start:` or `end:` value that matches none of the accepted formats, or that names an invalid date or time, SHALL leave that time unset. The entry itself SHALL still be recorded. A bare time in a note whose filename contains no `YYYY-MM-DD` date SHALL be treated as unparseable.

#### Scenario: Placeholder left in the log  {#s-7fb1}
*Verification*: **non-executable**
- **WHEN** a time log contains `* start: HH:MM`
- **THEN** the entry's start time SHALL be unset

#### Scenario: Out-of-range time  {#s-7645}
*Verification*: **non-executable**
- **WHEN** a time log in the note `2026-02-14 Sat.md` contains `* start: 25:00`
- **THEN** the entry's start time SHALL be unset

#### Scenario: Bare time in a note without a date in its name  {#s-bd15}
*Verification*: **non-executable**
- **WHEN** the note `project/notes.md` contains a time log with `* start: 09:10`
- **THEN** the entry's start time SHALL be unset

### Requirement: Daily template pre-fills bare time placeholders  {#r-37c7}
The shipped daily template SHALL pre-fill the time log's starter entry with bare time placeholders (`* start: HH:MM` and `* end:   HH:MM`), with no date.

#### Scenario: New daily note  {#s-7f7a}
*Verification*: **non-executable**
- **WHEN** a daily note for 2026-09-25 is created from the shipped daily template
- **THEN** its time log starter entry SHALL contain `* start: HH:MM` and `* end:   HH:MM`
- **AND** SHALL NOT contain `2026-09-25` on those lines

### Requirement: Entries without activity text are recorded  {#r-b895}
A time log entry SHALL be recorded when its activity line has activity text or at least one tag, or when the entry has a `start:` or `end:` line. An entry whose activity line has only tags, or is empty, SHALL count toward the day's totals and its tags toward time by tag, the same as any other entry. A bare `-` line with no tags and no `start:` or `end:` line SHALL be ignored.

#### Scenario: Tag-only entry  {#s-a81b}
*Verification*: **non-executable**
- **WHEN** the note `2026-09-25 Fri.md` has a log entry `- #proj-01 #research` with `* start: 09:00` and `* end: 10:00`
- **THEN** an entry SHALL be recorded from 09:00 to 10:00 with tags `proj-01` and `research`

#### Scenario: Empty activity line with times  {#s-80c4}
*Verification*: **non-executable**
- **WHEN** a log entry is `-` with `* start: 09:30` and `* end: 10:00`
- **THEN** an entry SHALL be recorded from 09:30 to 10:00 with no tags

#### Scenario: Stray empty bullet  {#s-e427}
*Verification*: **non-executable**
- **WHEN** a log contains a line `-` with no tags and no `start:` or `end:` line
- **THEN** no entry SHALL be recorded for it

### Requirement: Time Block table cells are highlighted  {#r-e44b}
In a daily note (a `.md` file under `plan/daily/`), the plugin SHALL highlight table cells in the `### Time Block` section, which ends at the next heading of level 1 to 3 or the end of the note. A cell is the text between two pipes on one line. The plugin SHALL give each kind of cell its own highlight group, `metaNotesTimeBlock` followed by `Mtg`, `Bracket`, `Tilde`, `Paren`, `Train`, `Pers` or `Work`, for a cell that contains `mtg:`, `[...]`, `~text~`, `(...)`, `train:`, `pers:` or `work:` respectively. A cell that matches several kinds SHALL take the one defined last (in the order listed, `Work` wins). The `~text~` in a cell SHALL also keep its `metaNotesOffPlan` strikethrough. Nothing outside the Time Block section, and nothing in a note that is not a daily note, SHALL get these highlights.

#### Scenario: Each kind of cell is highlighted  {#s-096b}
*Verification*: **non-executable**
- **WHEN** a daily note's Time Block has cells `mtg: standup`, `[break]`, `~walk~`, `(maybe)`, `train: x`, `pers: y` and `work: z`
- **THEN** each cell SHALL be highlighted with its group, and the pipes SHALL NOT

#### Scenario: Match does not cross pipes or lines  {#s-8148}
*Verification*: **non-executable**
- **WHEN** `mtg:` and a closing `]` are in different cells, or the two `~` are in different cells or on different lines
- **THEN** no cell SHALL be highlighted for that pair

#### Scenario: The heading keeps its heading highlight  {#s-6f8d}
*Verification*: **non-executable**
- **WHEN** a daily note has a `### Time Block` heading line
- **THEN** that line SHALL carry the markdown heading highlight (`markdownH3`) and NOT a `metaNotesTimeBlock` group, and the cells below it SHALL still be highlighted

#### Scenario: Outside the Time Block  {#s-a231}
*Verification*: **non-executable**
- **WHEN** the same cells are in another section of a daily note, or in a note that is not a daily note
- **THEN** they SHALL NOT be highlighted
