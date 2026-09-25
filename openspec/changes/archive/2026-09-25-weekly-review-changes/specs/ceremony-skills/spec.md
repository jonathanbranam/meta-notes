## MODIFIED Requirements

### Requirement: Weekly review
`weekly-review` SHALL review the workweek, Monday to Friday of the current week; weekend work is not covered. It SHALL draft from the week's completed tasks, time report, daily notes with their Follow up lists, and the notes changed that week from `meta-notes changes --date <Monday>..<Friday>`. From the change list it SHALL skip rename-only entries and daily and weekly plan notes, and SHALL use the remaining notes as prompts for work the other inputs missed, asking the user about any it can't place; it SHALL NOT match changed notes against tasks or time entries. The skill SHALL read git history only through `meta-notes changes`, and SHALL NOT run `git` or read file modification times itself. If `meta-notes changes` fails, the review SHALL continue without it. It SHALL cover plan versus actual, commitments (`#wait` tasks and things owed), project warnings from `meta-notes projects --warnings`, and a `#later` scan, where a task the user says is live gets `#later` removed and, if needed, a date. It SHALL write a summary for the user's manager in the weekly note's `## Review` section with exactly two parts: what was done this week and why it matters, then important upcoming dates and deadlines. The summary SHALL NOT include a plan for next week. The skill SHALL mark `review complete` and remind the user that weekly planning is next.

#### Scenario: Review period
- **WHEN** the weekly review runs on Friday 2026-09-25
- **THEN** it SHALL draft from 2026-09-21 through 2026-09-25, for example `meta-notes time --date 2026-09-21..2026-09-25`

#### Scenario: Changed notes gathered
- **WHEN** the weekly review runs on Friday 2026-09-25
- **THEN** it SHALL run `meta-notes changes --date 2026-09-21..2026-09-25 --json`

#### Scenario: Plan notes and archives skipped
- **WHEN** the change list has `plan/daily/26-Q3/2026-09-23.md`, `plan/week/26-Q3/2026-09-21.md`, a rename-only entry for `archive/project/trip.md`, and a modified `resource/design-doc.md`
- **THEN** the skill SHALL consider only `resource/design-doc.md`

#### Scenario: Unplaced change asked about
- **WHEN** `resource/design-doc.md` changed this week and the skill can't tell from the other inputs what the work was
- **THEN** the skill SHALL ask the user whether it belongs in the summary

#### Scenario: Changes unavailable
- **WHEN** `meta-notes changes` exits non-zero
- **THEN** the review SHALL continue from its other inputs and SHALL NOT run `git` itself

#### Scenario: Summary shape
- **WHEN** the weekly review writes its summary
- **THEN** the `## Review` section SHALL have a part on the week's work and why it matters and a part on upcoming dates and deadlines, and no next-week plan

#### Scenario: Live later task
- **WHEN** the user says a `#later` task is now live and due 2026-10-02
- **THEN** the skill SHALL run `task update` with `--remove-tag later --due 2026-10-02`
