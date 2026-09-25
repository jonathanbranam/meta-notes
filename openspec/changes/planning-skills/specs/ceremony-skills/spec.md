## Purpose

Specifies the shipped planning skills (daily shutdown, daily planning, weekly review, weekly planning, and task cleanup): what each reads and writes, how it hands off to the next ceremony, and the rules every skill follows so ceremonies stay short and edits stay safe.

## ADDED Requirements

### Requirement: Shipped skills
The plugin SHALL ship `daily-shutdown`, `daily-plan`, `weekly-review`, `weekly-plan`, and `task-cleanup` as `skills/<name>/SKILL.md`, installed into a notes root by `meta-notes init`. Each skill's description SHALL name when to use it, and SHALL NOT trigger on another skill's ceremony.

#### Scenario: Skills installed
- **WHEN** the user runs `meta-notes init` in a notes root
- **THEN** `.claude/skills/` SHALL contain all five skills

#### Scenario: Task cleanup request
- **WHEN** the user asks the agent to clean up stale tasks
- **THEN** the `task-cleanup` skill SHALL match the request

### Requirement: Skills start from the CLI
Every skill SHALL start by running `meta-notes conventions` and SHALL follow the conventions it prints. When `meta-notes` is not on `PATH`, the skill SHALL stop and tell the user how to install it, without reading or editing notes. Skills SHALL read notes through focused CLI queries (tags, folders, date ranges) and SHALL NOT read whole folders to find tasks.

#### Scenario: CLI missing
- **WHEN** a skill runs and `meta-notes` is not on `PATH`
- **THEN** the skill SHALL stop with a message saying to link `bin/meta-notes` into a directory on `PATH`, and SHALL NOT edit any file

### Requirement: Edits go through the CLI
Skills SHALL change task lines only with `meta-notes task update`, using the `file`, `line`, and `text` of a task from `meta-notes tasks --json`. When `task update` reports that the line changed, the skill SHALL re-query and retry with the current text, or ask the user. Skills SHALL move, rename, or archive notes only with `meta-notes move`, `rename`, and `archive`, and only after the user confirms the exact command. Skills SHALL add new lines (tasks, Follow up items, summaries) and set project fields by editing the note directly, putting tags before date markers and keeping lines within 80 columns.

#### Scenario: Stale line
- **WHEN** a skill runs `task update` and the command fails because the line changed since the query
- **THEN** the skill SHALL re-query that task before editing it again, and SHALL NOT rewrite the line by hand

#### Scenario: Structural change
- **WHEN** the user asks a skill to archive a note
- **THEN** the skill SHALL show the `meta-notes archive` command and run it only after the user confirms

### Requirement: Carrying a task forward
When a skill carries an unfinished task from one note to another, it SHALL write the new copy in the target note and mark the old line `>` with `meta-notes task update --status '>'`. It SHALL NOT move the original task's dates to the copy by editing the original.

#### Scenario: Unfinished daily task
- **WHEN** a task copied into Thursday's daily note was not done and the user carries it to Friday
- **THEN** Friday's note SHALL get a copy of the task, and Thursday's line SHALL have status `>`

### Requirement: Time budget and stopping early
Each skill SHALL state its time budget at the start. When the user says to stop, the skill SHALL save what has been decided so far, say what was left undone, and end without further questions. A ceremony that was stopped early SHALL NOT be marked complete, except where a skill below says otherwise.

#### Scenario: Stop during shutdown
- **WHEN** the user stops daily shutdown after the collect step
- **THEN** the tasks collected so far SHALL be saved, the remaining steps SHALL be listed, and `shutdown complete` SHALL stay unchecked

### Requirement: Ceremony completion and handoff
A skill that completes its ceremony SHALL check its marker with `meta-notes task update --status x`, which records the completion date. A ceremony with a successor SHALL end by offering it and SHALL NOT start it: daily shutdown offers daily planning, and weekly review reminds the user that weekly planning is next. Skills SHALL use `meta-notes ceremony status` to find skipped ceremonies they depend on and SHALL mention them without blocking.

#### Scenario: Shutdown offers planning
- **WHEN** daily shutdown completes
- **THEN** `shutdown complete` SHALL be checked with a `✅` date, and the skill SHALL offer to run daily planning without running it

#### Scenario: Skipped shutdown mentioned
- **WHEN** daily planning runs and the previous workday's shutdown is not done
- **THEN** the skill SHALL say so and continue

### Requirement: Daily shutdown
`daily-shutdown` SHALL close out today's daily note, in about 15 minutes, with these steps in order: collect (items the user pastes or names become tasks in the right note), PR check (each open PR needing the user becomes a task dated the next workday), a next step for each project worked on today, the time-log check, a Follow up list, commit, and mark `shutdown complete`. It SHALL NOT plan the next day. The time-log check SHALL run today's time report, find gaps and large stretches that don't clearly map to a project or work item, ask the user about each, and update the log from the answers. The Follow up list SHALL go in today's `## Follow Up` section and list what to pick up on the next workday. The commit SHALL include all note changes in the notes root and SHALL be made only after the user confirms it.

#### Scenario: Time-log gap
- **WHEN** today's time report shows no entry from 13:00 to 14:30
- **THEN** the skill SHALL ask what happened in that stretch and update the log from the answer

#### Scenario: Unclear entry
- **WHEN** a two-hour log entry has no project tag or link
- **THEN** the skill SHALL ask which project or work item it belongs to and update the entry

### Requirement: Daily planning
`daily-plan` SHALL plan one day in about 10–15 minutes. It SHALL plan today when today's daily note has no completed `plan complete` marker, and the next workday (Monday to Friday) otherwise, and SHALL state the choice. It SHALL always read the previous workday's note (its Follow up list, unfinished time blocks, and shutdown status), and for a Monday also the weekly plan. It SHALL gather meetings from a calendar screenshot the user provides, and due and overdue tasks and open `#wait` tasks from the CLI. It SHALL create the target day's note with `meta-notes note daily` if needed, fill the Plan column of the Time Block table, name a concrete first block, and mark `plan complete`. A Follow up item the user wants tracked SHALL become a task in place with `task update --due`. It SHALL NOT work through old tasks.

#### Scenario: Evening run after shutdown
- **WHEN** it is Thursday evening and Thursday's note has `- [x] plan complete`
- **THEN** the skill SHALL plan Friday

#### Scenario: Friday evening
- **WHEN** it is Friday evening and Friday is planned
- **THEN** the skill SHALL plan Monday and read the weekly plan for Monday's week

#### Scenario: Follow up item tracked
- **WHEN** the user wants the Follow up item `- [ ] reply to Sam` tracked for Monday 2026-09-28
- **THEN** the skill SHALL run `task update` on that line with `--due 2026-09-28`

### Requirement: Weekly review
`weekly-review` SHALL review the workweek, Monday to Friday of the current week; weekend work is not covered. It SHALL draft from the week's completed tasks, time report, and daily notes with their Follow up lists. It SHALL cover plan versus actual, commitments (`#wait` tasks and things owed), project warnings from `meta-notes projects --warnings`, and a `#later` scan, where a task the user says is live gets `#later` removed and, if needed, a date. It SHALL write a summary for the user's manager in the weekly note's `## Review` section with exactly two parts: what was done this week and why it matters, then important upcoming dates and deadlines. The summary SHALL NOT include a plan for next week. The skill SHALL mark `review complete` and remind the user that weekly planning is next.

#### Scenario: Review period
- **WHEN** the weekly review runs on Friday 2026-09-25
- **THEN** it SHALL draft from 2026-09-21 through 2026-09-25, for example `meta-notes time --date 2026-09-21..2026-09-25`

#### Scenario: Summary shape
- **WHEN** the weekly review writes its summary
- **THEN** the `## Review` section SHALL have a part on the week's work and why it matters and a part on upcoming dates and deadlines, and no next-week plan

#### Scenario: Live later task
- **WHEN** the user says a `#later` task is now live and due 2026-10-02
- **THEN** the skill SHALL run `task update` with `--remove-tag later --due 2026-10-02`

### Requirement: Weekly planning
`weekly-plan` SHALL plan the next workweek, Monday to Friday, from the weekly review and a calendar screenshot of that week. It SHALL work out capacity as free gaps of 90 minutes or more, listing shorter gaps separately, and SHALL list meetings to schedule and deadlines (`#deadline` tasks and due dates) landing in that week. It SHALL help the user choose 3–5 priorities, place them roughly on days, write the result in the next week's `## Plan` section (creating the note with `meta-notes note weekly` if needed), and mark that week's `plan complete`.

#### Scenario: Capacity
- **WHEN** Tuesday's calendar has free gaps of 2 hours and 45 minutes
- **THEN** the 2-hour gap SHALL count toward capacity and the 45-minute gap SHALL be listed separately

### Requirement: Task cleanup
`task-cleanup` SHALL be the only skill that works through old tasks. It SHALL list overdue open tasks across all notes, oldest due date first, then undated tasks grouped by note, in batches sized to the time the user has (5–10 minutes by default). For each task, the user SHALL choose keep, date it, `#later`, cancel, or done, applied with `task update`. For a batch, the skill SHALL also offer cancel all and later all, applied as one `task update` per line from the same query. Stopping early SHALL be safe; the next run starts again from the oldest tasks. It SHALL NOT use git history or file modification times.

#### Scenario: Later all
- **WHEN** the user chooses later all for a batch of five tasks from one query
- **THEN** the skill SHALL run five `task update --add-tag later` calls with the lines and text from that query
