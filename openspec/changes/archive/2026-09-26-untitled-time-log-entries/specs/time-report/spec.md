# Spec Delta

## MODIFIED Requirements

### Requirement: Day log listing
The day log listing SHALL list the day's time log entries in the order they appear in the note. Each entry SHALL show its activity line as written, followed by its `start` and `end` as `HH:MM`, its `time` (the duration, formatted `H hr M min`, or `M min` under an hour), and its `tags`. An entry missing a start or end time SHALL show `*MISSING START TIME*` or `*MISSING END TIME*` in place of that time and SHALL show no `time`.

#### Scenario: Complete entry
- **WHEN** the log has `- June DMC Connect #meeting` with `* start: 15:00` and `* end: 15:50`
- **THEN** the listing SHALL show `June DMC Connect #meeting` with `start: 15:00`, `end: 15:50`, `time: 50 min`, and tag `meeting`

#### Scenario: Entry over an hour
- **WHEN** an entry runs from 08:00 to 09:25
- **THEN** its `time` SHALL be `1 hr 25 min`

#### Scenario: Missing end time
- **WHEN** an entry has a start of 14:00 and no parseable end
- **THEN** it SHALL show `start: 14:00` and `*MISSING END TIME*`, and no `time`

#### Scenario: Tag-only entry
- **WHEN** the log has `- email #admin` from 08:30 to 09:00, `- #proj-01 #research` from 09:00 to 10:00, and `- code review #code` from 10:00 to 10:30
- **THEN** the listing SHALL show `- #proj-01 #research` with `start: 09:00`, `end: 10:00`, `time: 1 hr 0 min`, and tags `proj-01 research` between the other two
- **AND** no `*GAP` line SHALL be listed
- **AND** `total duration` SHALL be `2 hr 0 min` and no `*missing time*` line SHALL be shown
