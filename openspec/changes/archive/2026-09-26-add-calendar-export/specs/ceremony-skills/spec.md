## MODIFIED Requirements

### Requirement: Daily planning
`daily-plan` SHALL plan one day in about 10–15 minutes. It SHALL plan today when today's daily note has no completed `plan complete` marker, and the next workday (Monday to Friday) otherwise, and SHALL state the choice. It SHALL always read the previous workday's note (its Follow up list, unfinished time blocks, and shutdown status), and for a Monday also the weekly plan. It SHALL gather meetings for the target day as "Calendar from the export" requires, and due and overdue tasks and open `#wait` tasks from the CLI. It SHALL create the target day's note with `meta-notes note daily` if needed, fill the Plan column of the Time Block table, name a concrete first block, and mark `plan complete`. A Follow up item the user wants tracked SHALL become a task in place with `task update --due`. It SHALL NOT work through old tasks.

#### Scenario: Evening run after shutdown
- **WHEN** it is Thursday evening and Thursday's note has `- [x] plan complete`
- **THEN** the skill SHALL plan Friday

#### Scenario: Friday evening
- **WHEN** it is Friday evening and Friday is planned
- **THEN** the skill SHALL plan Monday and read the weekly plan for Monday's week

#### Scenario: Follow up item tracked
- **WHEN** the user wants the Follow up item `- [ ] reply to Sam` tracked for Monday 2026-09-28
- **THEN** the skill SHALL run `task update` on that line with `--due 2026-09-28`

#### Scenario: Meetings from the export
- **WHEN** the skill plans Monday 2026-09-28 and a current export exists
- **THEN** the skill SHALL run `meta-notes calendar --date 2026-09-28 --json` and use its meetings without asking for a screenshot

### Requirement: Weekly planning
`weekly-plan` SHALL plan the next workweek, Monday to Friday, from the weekly review and that week's calendar, gathered as "Calendar from the export" requires. It SHALL work out capacity as free gaps of 90 minutes or more, listing shorter gaps separately, and SHALL list meetings to schedule and deadlines (`#deadline` tasks and due dates) landing in that week. It SHALL help the user choose 3–5 priorities, place them roughly on days, write the result in the next week's `## Plan` section (creating the note with `meta-notes note weekly` if needed), and mark that week's `plan complete`.

#### Scenario: Capacity
- **WHEN** Tuesday's calendar has free gaps of 2 hours and 45 minutes
- **THEN** the 2-hour gap SHALL count toward capacity and the 45-minute gap SHALL be listed separately

#### Scenario: Week from the export
- **WHEN** the skill plans the week of 2026-09-28 and a current export exists
- **THEN** the skill SHALL run `meta-notes calendar --date 2026-09-28..2026-10-02 --json` and use its meetings without asking for a screenshot

## ADDED Requirements

### Requirement: Calendar from the export
A skill that needs meetings SHALL run `meta-notes calendar --date <period> --json` for the days it plans. When the command succeeds, the skill SHALL use its agenda, SHALL tell the user how old the export is, and SHALL pass on its warnings (a stale export, a missing export, `email` not set). When the command fails, the skill SHALL tell the user they can export from Google Calendar into the folder the error names, or provide a screenshot of the calendar for those days, and SHALL continue with whichever the user provides. It SHALL NOT ask for a screenshot when the command succeeds.

#### Scenario: Stale export
- **WHEN** the command succeeds with a warning that the export is 4 days old
- **THEN** the skill SHALL use the agenda and tell the user the export is 4 days old

#### Scenario: No export
- **WHEN** the command fails because no export was found
- **THEN** the skill SHALL name the `ics/` folder from the error and offer exporting there or providing a screenshot

#### Scenario: Calendar support not installed
- **WHEN** the command fails because calendar support is not installed
- **THEN** the skill SHALL say to run `meta-notes init` and SHALL continue from a screenshot if the user provides one
