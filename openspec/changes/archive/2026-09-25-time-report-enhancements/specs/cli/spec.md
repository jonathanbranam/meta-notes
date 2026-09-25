## ADDED Requirements

### Requirement: Time report command
The CLI SHALL provide `meta-notes time [--date DATE] [--json]`, which prints the time report specified in `time-report` for the notes root. It SHALL resolve the notes root like the other commands. It SHALL read notes and SHALL NOT write or change any file.

#### Scenario: Time report from a subfolder
- **WHEN** `meta-notes time --date 2026-09-22` is run from `project/foo/` inside a notes root
- **THEN** it SHALL print the day report for `plan/daily/26-Q3/2026-09-22 Tue.md` in that notes root

#### Scenario: Time report error as JSON
- **WHEN** `meta-notes time --date next-week --json` is run
- **THEN** it SHALL exit non-zero and write one JSON object with `ok` false and an `error` naming `next-week`

#### Scenario: Read only
- **WHEN** `meta-notes time` is run in a notes root
- **THEN** no file in the notes root SHALL be created, changed, or removed
