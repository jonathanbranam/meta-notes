# checkin Specification

## Purpose
Specifies stay-on-task check-ins: `meta-notes checkin wait`, which sleeps until a check-in is due and then exits so a calling agent wakes; `meta-notes checkin status`, which reports the daily note's Time Block without sleeping; `meta-notes checkin actual`, which fills the Time Block's Actual column; and the `checkin` skill that uses them to ask the user for progress updates and help with task switching. Nothing here needs hooks or a daemon: the agent runs `wait` as a background command and Claude Code wakes it when the command exits.

## Requirements

### Requirement: Time Block rows
The Time Block SHALL be the table under the `### Time Block` heading of the daily note, ending at the next heading of level 1 to 3 or the end of the note. A row SHALL be a table line whose first cell is a 12-hour time such as `8:00am` or `12:15pm`; its second cell is the Plan and its third the Actual. A cell SHALL count as empty when it is blank. Header, separator and other lines SHALL be ignored. A daily note with no Time Block, or a Time Block with no rows, SHALL be reported as having no rows, and SHALL NOT be an error.

#### Scenario: Rows parsed
*Verification*: **non-executable**
- **WHEN** the Time Block has the line `|  9:15am | mtg: standup | reviewed PRs |`
- **THEN** the row SHALL have time 09:15, plan `mtg: standup` and actual `reviewed PRs`

#### Scenario: No Time Block
*Verification*: **non-executable**
- **WHEN** the daily note has no `### Time Block` heading
- **THEN** the report SHALL have no rows and the command SHALL succeed

### Requirement: Check-in status
`meta-notes checkin status [--date DAY] [--at HH:MM]` SHALL report, for the daily note of DAY (default today) at the time HH:MM (24-hour, default now), without writing any file: the note path and whether it exists; the current row, the last row whose time is at or before HH:MM, with its plan and actual; and the unfilled rows. The unfilled rows SHALL be the rows before the current row that have an empty Actual, counted from the row after the last row with a non-empty Actual that is at or before HH:MM, or, when no Actual is filled, from the first row with a non-empty Plan. A DAY that is a range or other period form SHALL be a usage error. With `--json` the result SHALL have `date`, `time`, `note`, `note_exists`, `current` (`time`, `plan`, `actual`, or null when there is none) and `unfilled` (a list of `time` and `plan`). The text output SHALL be a line with the time and current plan, followed by one line per unfilled row.

#### Scenario: Unfilled rows since the last update
*Verification*: **non-executable**
- **WHEN** the rows 9:00am to 9:45am have Actual filled only at 9:00am, the Plan at 9:30am is `write spec`, and the user runs `meta-notes checkin status --at 10:05`
- **THEN** the current row SHALL be 10:00am, and the unfilled rows SHALL be 9:15am, 9:30am, 9:45am, with 9:30am's plan `write spec`

#### Scenario: Nothing filled yet
*Verification*: **non-executable**
- **WHEN** no Actual is filled, the first non-empty Plan is at 9:00am, and the time is 9:50
- **THEN** the unfilled rows SHALL begin at 9:00am and end at 9:30am

#### Scenario: Before the first row
*Verification*: **non-executable**
- **WHEN** the time is earlier than every row
- **THEN** `current` SHALL be null and `unfilled` SHALL be empty

#### Scenario: Missing note
*Verification*: **non-executable**
- **WHEN** the daily note does not exist
- **THEN** the command SHALL succeed with `note_exists` false, `current` null and no unfilled rows

### Requirement: Check-in wait
`meta-notes checkin wait [--every MINUTES] [--end HH:MM] [--date DAY]` SHALL sleep until the next check-in is due and then print the same report as `checkin status` for that time, plus `reason`, and exit 0. A check-in SHALL be due MINUTES minutes after the command starts, or at HH:MM if that is earlier. `reason` SHALL be `due` for the first and `end` for the second; when the command starts at or after HH:MM it SHALL report `end` at once without sleeping. MINUTES SHALL default to the `[checkin]` table's `interval` (default 30) and HH:MM to its `end` (default `17:30`). The command SHALL measure time by the clock rather than by counting sleeps, so that a sleeping machine wakes to a due check-in. The command SHALL NOT write any file, and SHALL always end, by the end time at the latest.

#### Scenario: Interval elapses
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes checkin wait --every 30` at 10:00 with the end at 17:30
- **THEN** the command SHALL exit at 10:30 with `reason` `due` and the status for 10:30

#### Scenario: Day ends first
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes checkin wait --every 30 --end 17:30` at 17:10
- **THEN** the command SHALL exit at 17:30 with `reason` `end`

#### Scenario: Already past the end
*Verification*: **non-executable**
- **WHEN** the command starts at 17:45 with the end at 17:30
- **THEN** it SHALL exit at once with `reason` `end`

#### Scenario: Interval from config
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has `[checkin]` with `interval = 20` and the user runs `meta-notes checkin wait` without `--every`
- **THEN** the check-in SHALL be due 20 minutes after the command starts

#### Scenario: Invalid interval
*Verification*: **non-executable**
- **WHEN** MINUTES is not a positive integer, or HH:MM is not a time
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Filling the Actual column
`meta-notes checkin actual TIME TEXT [--through TIME] [--force]` SHALL write TEXT into the Actual cell of the row at TIME, or of every row from TIME through `--through`, in today's daily note (or DAY's, with `--date`). TIME SHALL be 24-hour `HH:MM` or 12-hour such as `9:15am`, and SHALL name a row of the Time Block. A cell that is not empty SHALL NOT be changed unless `--force` is given; the command SHALL skip it and report it as skipped. A `|` in TEXT SHALL be written as `/`, and newlines as spaces. The cell SHALL be padded to its column's width when TEXT fits, and otherwise written as is, and no other cell or line SHALL change. A TIME that is not a row, a note without the row, or an empty TEXT SHALL be an error, and nothing SHALL be written. With `--json` the result SHALL have `note`, `written` (a list of times) and `skipped` (a list of times).

#### Scenario: One row
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes checkin actual 9:15 "reviewed PRs"` and the 9:15am Actual is empty
- **THEN** that row SHALL read `|  9:15am | <plan> | reviewed PRs                 |` and every other line SHALL be unchanged

#### Scenario: A range
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes checkin actual 09:00 "deep work on spec" --through 09:45`
- **THEN** the Actual of the rows 9:00am, 9:15am, 9:30am and 9:45am SHALL each be `deep work on spec`

#### Scenario: Filled cell kept
*Verification*: **non-executable**
- **WHEN** the row's Actual is `email` and the user runs the command without `--force`
- **THEN** the cell SHALL stay `email` and the row's time SHALL be listed as skipped

#### Scenario: Not a row
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes checkin actual 7:00am "x"` and there is no 7:00am row
- **THEN** the command SHALL exit non-zero and no file SHALL change

#### Scenario: Pipe in the text
*Verification*: **non-executable**
- **WHEN** TEXT is `a | b`
- **THEN** the cell SHALL contain `a / b`

### Requirement: Check-in skill
The plugin SHALL ship the `checkin` skill as `skills/checkin/SKILL.md`, installed by `meta-notes init` with the other skills. The skill SHALL start as the other skills do (`meta-notes` on `PATH`, then `meta-notes conventions`). It SHALL run `meta-notes checkin wait --json` as a background command and end its turn until the command exits, and SHALL NOT poll, sleep, or use hooks. When woken it SHALL read the report and ask the user one short question: whether they are on the current row's plan, and what they did since the last update. It SHALL write the answer with `meta-notes checkin actual`, ask what is next when the user changed tasks, and then start `wait` again. It SHALL stop starting waits when the user says stop or the reason is `end`, and then offer `daily-shutdown`. It SHALL NOT edit any other part of a note, and SHALL NOT nag: a declined or unanswered check-in is skipped. The skill's description SHALL name check-ins and staying on task, and SHALL NOT trigger on another skill's ceremony.

#### Scenario: Skill installed
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes init` in a notes root
- **THEN** `.claude/skills/` SHALL contain `checkin`

#### Scenario: Check-in due
*Verification*: **non-executable**
- **WHEN** the background `wait` exits with `reason` `due`, the current row's plan is `write spec`, and the user answers "finished the outline"
- **THEN** the skill SHALL run `checkin actual` for the unfilled rows and the current row with that answer, and start another `wait`

#### Scenario: End of day
*Verification*: **non-executable**
- **WHEN** `wait` exits with `reason` `end`
- **THEN** the skill SHALL not start another `wait`, and SHALL offer `daily-shutdown`
