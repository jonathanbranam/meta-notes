# time-report Specification

## Purpose
Specifies the time report built from daily-note time logs: selecting a day or period with `--date`, listing a day's log with its gaps, overlaps, and missing time, and summarizing a week or longer period by tag and by day. Entry syntax and timestamp formats are specified in `time-log`.

## Requirements

### Requirement: Report selected by date or file  {#r-a24a}
`meta-notes time` and `scripts/time_report.py` SHALL accept `--date` in the `date-period` syntax, defaulting to today. The daily note for a date SHALL be `plan/daily/YY-Qn/YYYY-MM-DD Ddd.md` under the notes root. `scripts/time_report.py` SHALL also keep accepting a daily note's path as a positional argument, which selects that note's day. Giving both a file and `--date` SHALL be an error.

A period whose START equals its END SHALL produce the day report for that date. Any longer period SHALL produce the period report.

#### Scenario: Report for a date  {#s-47ff}
*Verification*: **non-executable**
- **WHEN** `python3 scripts/time_report.py --date 2026-09-22` is run in a notes root that contains `plan/daily/26-Q3/2026-09-22 Tue.md`
- **THEN** it SHALL print the day report for that note

#### Scenario: Report for a file  {#s-de0c}
*Verification*: **non-executable**
- **WHEN** `python3 scripts/time_report.py "plan/daily/26-Q3/2026-09-22 Tue.md"` is run
- **THEN** it SHALL print the same day report as `--date 2026-09-22`

#### Scenario: Default date  {#s-0a47}
*Verification*: **non-executable**
- **WHEN** `meta-notes time` is run on 2026-09-25 with no `--date`
- **THEN** it SHALL print the day report for 2026-09-25

#### Scenario: Missing daily note  {#s-edad}
*Verification*: **non-executable**
- **WHEN** a single-day `--date` names a date with no daily note
- **THEN** the command SHALL exit non-zero with an error naming the expected daily note path

#### Scenario: File and date together  {#s-6eed}
*Verification*: **non-executable**
- **WHEN** `time_report.py` is given both a file and `--date`
- **THEN** it SHALL exit non-zero with an error and print no report

#### Scenario: Invalid date  {#s-43af}
*Verification*: **non-executable**
- **WHEN** `--date 2026-02-30` is given
- **THEN** the command SHALL exit non-zero with the `date-period` invalid-period error

### Requirement: Day report layout  {#r-4019}
The day report SHALL contain, in order: the day log listing, the day's Total Time section, time by tag, work vs. non-work, plan adherence, and the summary for the Monday–Sunday week containing the day.

#### Scenario: Section order  {#s-1d15}
*Verification*: **non-executable**
- **WHEN** a day report is printed for a note with a time log and a time block
- **THEN** the day log listing SHALL come first, followed by Total Time, time by tag, work vs. non-work, plan adherence, and the week summary

#### Scenario: Note with no log  {#s-8f1e}
*Verification*: **non-executable**
- **WHEN** the daily note has no time log entries
- **THEN** the day log listing SHALL say no time log entries were found, and the plan adherence and week summary sections SHALL still be printed

### Requirement: Day log listing  {#r-191f}
The day log listing SHALL list the day's time log entries in the order they appear in the note. Each entry SHALL show its activity line as written, followed by its `start` and `end` as `HH:MM`, its `time` (the duration, formatted `H hr M min`, or `M min` under an hour), and its `tags`. An entry missing a start or end time SHALL show `*MISSING START TIME*` or `*MISSING END TIME*` in place of that time and SHALL show no `time`.

#### Scenario: Complete entry  {#s-91da}
*Verification*: **non-executable**
- **WHEN** the log has `- June DMC Connect #meeting` with `* start: 15:00` and `* end: 15:50`
- **THEN** the listing SHALL show `June DMC Connect #meeting` with `start: 15:00`, `end: 15:50`, `time: 50 min`, and tag `meeting`

#### Scenario: Entry over an hour  {#s-be84}
*Verification*: **non-executable**
- **WHEN** an entry runs from 08:00 to 09:25
- **THEN** its `time` SHALL be `1 hr 25 min`

#### Scenario: Missing end time  {#s-bb2a}
*Verification*: **non-executable**
- **WHEN** an entry has a start of 14:00 and no parseable end
- **THEN** it SHALL show `start: 14:00` and `*MISSING END TIME*`, and no `time`

#### Scenario: Tag-only entry  {#s-1260}
*Verification*: **non-executable**
- **WHEN** the log has `- email #admin` from 08:30 to 09:00, `- #proj-01 #research` from 09:00 to 10:00, and `- code review #code` from 10:00 to 10:30
- **THEN** the listing SHALL show `- #proj-01 #research` with `start: 09:00`, `end: 10:00`, `time: 1 hr 0 min`, and tags `proj-01 research` between the other two
- **AND** no `*GAP` line SHALL be listed
- **AND** `total duration` SHALL be `2 hr 0 min` and no `*missing time*` line SHALL be shown

### Requirement: Gaps and overlaps between entries  {#r-e0a5}
For each pair of consecutive entries in the listing where the earlier entry has an end time and the later entry has a start time, the gap SHALL be the later start minus the earlier end, in whole minutes. A gap of more than 2 minutes SHALL be listed between the two entries as `*GAP of N min*`, with `start` set to the earlier entry's end and `end` set to the later entry's start. A negative gap SHALL be listed as `*Overlap of N min*`, where N is the size of the overlap, with `start` set to the earlier entry's end and `end` set to the later entry's start. A gap from 0 to 2 minutes SHALL NOT be listed. No gap or overlap SHALL be computed across an entry that is missing the needed time.

#### Scenario: Gap  {#s-deca}
*Verification*: **non-executable**
- **WHEN** one entry ends at 15:50 and the next starts at 16:00
- **THEN** `*GAP of 10 min*` with `start: 15:50` and `end: 16:00` SHALL appear between them

#### Scenario: Small gap ignored  {#s-6582}
*Verification*: **non-executable**
- **WHEN** one entry ends at 10:00 and the next starts at 10:02
- **THEN** no gap SHALL be listed between them

#### Scenario: Overlap  {#s-60fc}
*Verification*: **non-executable**
- **WHEN** one entry ends at 14:39 and the next starts at 14:30
- **THEN** `*Overlap of 9 min*` with `start: 14:39` and `end: 14:30` SHALL appear between them

#### Scenario: Missing time breaks the chain  {#s-2d58}
*Verification*: **non-executable**
- **WHEN** an entry has no end time and the next entry starts 30 minutes after the earlier entry's start
- **THEN** no gap or overlap SHALL be listed between them

### Requirement: Day totals and missing time  {#r-ff14}
The day's Total Time section SHALL report:
- `work duration`: time in the work window, excluding `#break`, `#off-task`, and `#personal` entries. The work window runs from the first to the last entry that is not tagged `#personal`, so leading and trailing `#personal` entries are stripped.
- `total duration`: the sum of every entry's duration.
- `earliest time` and `latest time`: the earliest start and latest end of any entry.
- `total time`: the span from `earliest time` to `latest time`.
- `*missing time*`: `total time` minus `total duration`, shown only when it exceeds 10 minutes.

Tags SHALL be compared by their canonical names, so `#pers` and `#per` count as `#personal`.

#### Scenario: Missing time reported  {#s-a918}
*Verification*: **non-executable**
- **WHEN** the earliest start is 07:08, the latest end is 17:51, and the entries' durations sum to 9 hr 6 min
- **THEN** `total time` SHALL be `10 hr 43 min` and `*missing time*` SHALL be `1 hr 37 min`

#### Scenario: Missing time under threshold  {#s-3e9b}
*Verification*: **non-executable**
- **WHEN** `total time` exceeds `total duration` by 10 minutes or less
- **THEN** no `*missing time*` line SHALL be shown

#### Scenario: Personal time at the day's edges  {#s-8299}
*Verification*: **non-executable**
- **WHEN** a day starts with a 07:00–08:00 `#pers` entry, ends with an 18:00–19:00 `#personal` entry, and has two hours of untagged work between them
- **THEN** `work duration` SHALL be `2 hr 0 min` and `total duration` SHALL be `4 hr 0 min`

The Work vs Non-Work section SHALL use the same rule as `work duration`: an entry is non-work when it has any of `#break`, `#off-task` or `#personal`, and work otherwise, untagged entries included. Every timed entry counts, so the two add up to the total logged time.

#### Scenario: Work vs Non-Work agrees with work duration  {#s-f747}
*Verification*: **non-executable**
- **WHEN** a day has 90 minutes of untagged entries, a 15-minute `#pers` entry and a 30-minute `#break` entry
- **THEN** Work vs Non-Work SHALL show work 1 hr 30 min, non-work 45 min and total logged 2 hr 15 min

### Requirement: Period summary  {#r-c729}
A period summary SHALL cover every day from START to END. A week summary SHALL be the period summary for Monday through Sunday of the week. The summary SHALL be headed `Summary for <START> to <END>` and SHALL contain, in order:

1. **Total Time**: the period's `work duration` and `total duration` (the sums of each day's values), followed by the highlighted tags.
2. **Time per tag**: every canonical tag that has time in the period, sorted alphabetically, with its total duration. An entry with several tags SHALL count toward each of them.
3. **Day Summaries**: one item per day, with the date and day abbreviation. A day with time log entries SHALL show `work duration`, `earliest time`, `latest time`, and `total time`. A day with no daily note, or no time log entry with a start or end time (such as a note holding only the template's `HH:MM` placeholders), SHALL show `(no log)`.

Tag names SHALL be shown without `#`.

#### Scenario: Weekly span  {#s-1f35}
*Verification*: **non-executable**
- **WHEN** the day report is printed for Thursday 2026-09-24
- **THEN** the week summary SHALL be headed `Summary for 2026-09-21 to 2026-09-27` and list seven days, Monday through Sunday

#### Scenario: Weekend entries counted  {#s-24a9}
*Verification*: **non-executable**
- **WHEN** Saturday's note in the week has a one-hour `#code` entry
- **THEN** that hour SHALL count in the week's `total duration` and in the `code` tag total

#### Scenario: Aliases combined  {#s-b08c}
*Verification*: **non-executable**
- **WHEN** one entry in the week is tagged `#mtg` for 30 minutes and another is tagged `#meeting` for 1 hour
- **THEN** Time per tag SHALL list `meeting: 1 hr 30 min` and SHALL NOT list `mtg`

#### Scenario: Day with no log  {#s-a438}
*Verification*: **non-executable**
- **WHEN** a day in the period has no daily note
- **THEN** its Day Summaries item SHALL show `(no log)`

#### Scenario: Day with only placeholder entries  {#s-fa55}
*Verification*: **non-executable**
- **WHEN** a day's note has time log entries but none has a parseable start or end time
- **THEN** its Day Summaries item SHALL show `(no log)`

#### Scenario: Month period  {#s-6972}
*Verification*: **non-executable**
- **WHEN** `meta-notes time --date 2026-09` is run
- **THEN** it SHALL print the period summary headed `Summary for 2026-09-01 to 2026-09-30`, with one Day Summaries item for each of the 30 days

### Requirement: Highlighted tags  {#r-73dd}
The Total Time section of a period summary SHALL list, after `work duration` and `total duration`, a fixed list of highlighted tags with display labels, in this order:

| Label | Counts |
|---|---|
| all meetings | the `Meeting` tag group |
| recruiting | `recruiting` |
| agile | `agile` |
| fence | `fence` |
| iceberg | `iceberg` |
| code | `code` |
| integr-test | `integr-test` |
| axe | `axe` |
| off-task | `off-task` |

A highlighted item that names a tag group SHALL total the time of entries carrying any tag in that group, counting each entry once. Only highlighted items with time in the period SHALL be shown.

#### Scenario: Highlighted tag shown  {#s-aaf4}
*Verification*: **non-executable**
- **WHEN** the week has 2 hr 25 min of `#meeting` entries and 22 min of `#recruiting` entries, and none of the other highlighted tags
- **THEN** Total Time SHALL list `all meetings: 2 hr 25 min` and `recruiting: 22 min`, in that order, and no other highlighted items

#### Scenario: Group counts an entry once  {#s-07de}
*Verification*: **non-executable**
- **WHEN** an entry tagged both `#meeting` and `#mtg` runs 30 minutes
- **THEN** it SHALL add 30 minutes to `all meetings`

### Requirement: Time report JSON  {#r-d047}
With `--json`, `meta-notes time` SHALL return the report's data as one JSON object with `ok` true, `start` and `end` dates, `report` (the text report, identical to the output without `--json`), and `warnings`. A day report SHALL also include the day's `entries` in listing order, each gap and overlap in that listing marked by its kind, the day totals, time by tag, work vs. non-work, plan adherence, and the week summary. A period report SHALL include the period summary. Times SHALL be `HH:MM`, dates `YYYY-MM-DD`, and durations whole minutes. Tags SHALL be canonical names without `#`.

#### Scenario: Entry fields  {#s-ed57}
*Verification*: **non-executable**
- **WHEN** `meta-notes time --date 2026-09-22 --json` is run and the day's first entry is `June DMC Connect #meeting` from 15:00 to 15:50
- **THEN** the first item of `entries` SHALL have the activity line, `start` `15:00`, `end` `15:50`, `minutes` 50, and `tags` `["meeting"]`

#### Scenario: Gap in JSON  {#s-1aa8}
*Verification*: **non-executable**
- **WHEN** the day has a 10-minute gap between two entries
- **THEN** the listing SHALL include an item of kind `gap` with 10 minutes and the two boundary times, between the two entries

#### Scenario: Text report in JSON  {#s-6094}
*Verification*: **non-executable**
- **WHEN** `meta-notes time --date 2026-09-22 --json` is run
- **THEN** its `report` SHALL equal the stdout of `meta-notes time --date 2026-09-22` without its trailing newline

#### Scenario: Missing times in JSON  {#s-c809}
*Verification*: **non-executable**
- **WHEN** an entry has no end time
- **THEN** its `end` and `minutes` SHALL be null

### Requirement: Vim time report uses the CLI  {#r-7dc8}
`:MetaNotesTimeReport` SHALL get its report from `meta-notes time` with `--date` set to the current daily note's date and SHALL show it in the `Time Report` buffer as before. It SHALL still be available only in daily notes. If the CLI fails, it SHALL show the error with the error highlight and SHALL NOT raise a Vim exception.

#### Scenario: Report from a daily note  {#s-923b}
*Verification*: **non-executable**
- **WHEN** the user runs `:MetaNotesTimeReport` in `plan/daily/26-Q3/2026-09-22 Tue.md`
- **THEN** the `Time Report` buffer SHALL show the output of `meta-notes time --date 2026-09-22`

#### Scenario: Outside a daily note  {#s-0b1b}
*Verification*: **non-executable**
- **WHEN** the user runs `:MetaNotesTimeReport` in a project note
- **THEN** it SHALL show an error saying the command is only available in daily notes

### Requirement: Time report follows the root mode  {#r-2a1b}
`meta-notes time` SHALL read the notes root's mode (`mode` in `.meta-notes`, default `work`; see `design/specs/notes-config.md`) and include it as `mode` in its JSON. In a `work` root, every requirement above applies unchanged. In a `personal` root, untagged time is personal and `#work` marks work time:
- There is no work window: `#personal` entries are not trimmed from the day's ends, and `work duration` is not shown, in the day, period or day-summary sections. The JSON `work_minutes` is the time tagged `#work`.
- The day report's Work vs Non-Work section SHALL be replaced by a `### Day Total` section with `Total logged` and, when there is `#work` time, a `Work` line. The JSON `work_vs_nonwork` is null and `day_total` has `total_minutes` and `work_minutes`. Time by Tag is the breakdown by tag.
- The highlighted tags SHALL be, in this order and with the tag's name as label, `exercise`, `family`, `maint` and `work`; there are no tag groups.
- Tag aliases SHALL be `#mtg` for `#meeting`, `#waiting` for `#wait`, and `#wk` for `#work`; `#pers` and `#per` are not aliases of `#personal`.

The lists are fixed per mode, not configuration.

#### Scenario: Personal untagged time  {#s-1ed4}
*Verification*: **non-executable**
- **WHEN** a day in a personal root has 1 hr untagged, 2 hr `#work` and 1 hr `#exercise`
- **THEN** the report SHALL show no `work duration` and no Work vs Non-Work, and `### Day Total` SHALL show `Total logged: 4h 0m` and `Work: 2h 0m`

#### Scenario: Work mode unchanged  {#s-8b6e}
*Verification*: **non-executable**
- **WHEN** the root has no `mode`, or `mode = "work"`
- **THEN** the report SHALL be as before, with `work duration` and Work vs Non-Work
