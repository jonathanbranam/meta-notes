# ceremony-status Specification

## Purpose
Specifies the ceremony markers in daily and weekly notes and `meta-notes ceremony status`, which reports which ceremonies are done for a day and its week, so skills, reminders, and the dashboard can find skipped steps.

## Requirements

### Requirement: Ceremony markers
A ceremony marker SHALL be a checkbox line whose text, after the checkbox and without a trailing `✅` date, is the marker name, compared ignoring case and surrounding whitespace. The daily note's markers SHALL be `plan complete` (daily planning) and `shutdown complete` (daily shutdown). The weekly note's markers SHALL be `review complete` (weekly review) and `plan complete` (weekly planning). A marker SHALL count as done when its status is `x` or `X`, with or without a trailing `✅` date, and SHALL NOT count as done for any other status. A marker SHALL be found anywhere in its note. When a note has several lines for the same marker, the marker SHALL be done if any of them is done.

#### Scenario: Checked marker with a completion date
- **WHEN** the daily note for 2026-09-25 has the line `- [x] shutdown complete ✅ 2026-09-26`
- **THEN** daily shutdown for 2026-09-25 SHALL be done, with completion date 2026-09-26

#### Scenario: Checked marker without a completion date
- **WHEN** the daily note for 2026-09-25 has the line `- [x] plan complete`
- **THEN** daily planning for 2026-09-25 SHALL be done, with no completion date

#### Scenario: Unchecked or canceled marker
- **WHEN** the daily note has `- [ ] shutdown complete` or `- [-] shutdown complete`
- **THEN** daily shutdown SHALL NOT be done

#### Scenario: Marker missing
- **WHEN** a daily note created before this change has no `shutdown complete` line
- **THEN** daily shutdown SHALL NOT be done, and the result SHALL say the marker is missing

### Requirement: Ceremony status command
`meta-notes ceremony status [--date DAY]` SHALL report, for the day DAY and the Monday-to-Sunday week containing it, the four ceremonies: daily planning and daily shutdown from DAY's daily note, and weekly review and weekly planning from that week's weekly note. DAY SHALL be a single `YYYY-MM-DD` date and SHALL default to today; a range or other period form SHALL be a usage error. The note paths SHALL be the ones `meta-notes note daily` and `meta-notes note weekly` use for that date. For each ceremony, the result SHALL give the note path, whether the note exists, whether the marker is present, whether it is done, and its completion date when it has one. A missing note SHALL make its ceremonies not done, and SHALL NOT be an error. The command SHALL NOT write any file.

#### Scenario: All four ceremonies
- **WHEN** the daily note for 2026-09-25 has `- [x] plan complete` and `- [ ] shutdown complete`, the weekly note for the week of 2026-09-21 has `- [x] review complete ✅ 2026-09-25` and `- [ ] plan complete`, and the user runs `meta-notes ceremony status --date 2026-09-25`
- **THEN** daily planning and weekly review SHALL be reported done, and daily shutdown and weekly planning SHALL be reported not done

#### Scenario: Missing weekly note
- **WHEN** no weekly note exists for the week containing 2026-09-25 and the user runs `meta-notes ceremony status --date 2026-09-25`
- **THEN** the command SHALL succeed, and weekly review and weekly planning SHALL be reported not done with the note reported as missing

#### Scenario: Range rejected
- **WHEN** the user runs `meta-notes ceremony status --date 2026-09-21..2026-09-25`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Ceremony status output
The text output SHALL be one line per ceremony with its name, `done` or `not done`, and the completion date when there is one, followed by `(no note)` or `(no marker)` when the note or marker is missing. With `--json`, the result SHALL have `date`, `week_start`, and a `ceremonies` list, each entry with `name` (`daily-plan`, `daily-shutdown`, `weekly-review`, `weekly-plan`), `note`, `note_exists`, `marker_present`, `done`, and `completed` (a date or null).

#### Scenario: JSON result
- **WHEN** the user runs `meta-notes ceremony status --date 2026-09-25 --json` and the daily note has `- [x] shutdown complete ✅ 2026-09-25`
- **THEN** the `daily-shutdown` entry SHALL have `done` true and `completed` `2026-09-25`, and `week_start` SHALL be `2026-09-21`
