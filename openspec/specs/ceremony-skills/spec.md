# ceremony-skills Specification

## Purpose
Specifies the shipped planning skills (daily shutdown, daily planning, weekly review, weekly planning, task cleanup, and project review): what each reads and writes, how it hands off to the next ceremony, and the rules every skill follows so ceremonies stay short and edits stay safe.

## Requirements

### Requirement: Shipped skills
The plugin SHALL ship `daily-shutdown`, `daily-plan`, `weekly-review`, `weekly-plan`, `task-cleanup`, and `project-review` as `skills/<name>/SKILL.md`, installed into a notes root by `meta-notes init`. Each skill's description SHALL name when to use it, and SHALL NOT trigger on another skill's ceremony.

#### Scenario: Skills installed
- **WHEN** the user runs `meta-notes init` in a notes root
- **THEN** `.claude/skills/` SHALL contain all six skills

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

### Requirement: Project review
`project-review` SHALL review one project per run, in 5–10 minutes, reading its state with `meta-notes project brief`. Its description SHALL NOT trigger on task cleanup. It SHALL NOT propose other projects to review. It SHALL show the project's files and tasks, open and completed, and give its state in about ten lines. It SHALL NOT walk through the project's stale tasks one by one; it leaves that to `task-cleanup`.

#### Scenario: Task cleanup request
- **WHEN** the user asks the agent to clean up stale tasks
- **THEN** `project-review` SHALL NOT match the request

### Requirement: Project review selection
With no project named, `project-review` SHALL pick from `meta-notes projects --json`, leaving out projects with status `done`, the project with the oldest last review, preferring never-reviewed projects, and taking ties in the list's order. When the picked project's brief has an open `#review` task due after today, the skill SHALL pass over it and take the next candidate, without listing the candidates. A project the user names SHALL be reviewed whatever its status or scheduled reviews.

#### Scenario: Oldest review picked
- **WHEN** no project is named and `meta-notes projects` shows one project never reviewed and others reviewed
- **THEN** the skill SHALL review the never-reviewed project without listing the others

#### Scenario: Done project skipped
- **WHEN** no project is named and the only never-reviewed project has status `done`
- **THEN** the skill SHALL pick among the other projects by oldest last review

#### Scenario: Scheduled review honored
- **WHEN** today is 2026-09-25, no project is named, and the project with the oldest review has `- [ ] project #review 📅 2026-11-01`
- **THEN** the skill SHALL review the project with the next oldest review

### Requirement: Project review disposition
`project-review` SHALL ask for a disposition: continue, pause, done, convert to area, split, or merge. Pause SHALL set the `status` field to `paused` and offer to add an open `#review` task dated for when to reconsider the project. Done SHALL set the `status` field to `done` and offer to run `meta-notes archive` on the project; when declined, the project stays in `project/`. Convert to area SHALL use `meta-notes move` to `area/`. Split and merge SHALL carry tasks between projects as "Carrying a task forward" requires, create any new project note with `meta-notes note new`, and move notes only with `meta-notes move`. Every `archive`, `move`, and `note new` SHALL run only after the user confirms the exact command. When the project stays active and has no open `#next`, the skill SHALL ask for a next action, accepting none as an answer; it SHALL NOT ask for other dispositions.

#### Scenario: Pause
- **WHEN** the user pauses the project
- **THEN** the home note's `status` field SHALL become `paused`, and the skill SHALL offer to add a dated `#review` task for when to reconsider it

#### Scenario: Done
- **WHEN** the user marks the project done
- **THEN** the home note's `status` field SHALL become `done`, the skill SHALL show the `meta-notes archive` command for the project, and SHALL run it only if the user confirms

#### Scenario: No next action asked for a done project
- **WHEN** the user marks a project with no open `#next` done
- **THEN** the skill SHALL NOT ask for a next action

### Requirement: Project review record
`project-review` SHALL record the review as a completed `#review` task in the home note. It SHALL check off, with `meta-notes task update --status x`, an open `#review` task in the home note that is undated or due on or before today, the earliest when there are several. With none, it SHALL add `- [ ] project #review 📅` to the home note, take the new line's `file`, `line`, and `text` from a fresh `meta-notes project brief --json`, and check it off the same way. Open `#review` tasks due after today SHALL be left open. When a folder project has no home note, the skill SHALL offer to create `Home.md` with a title and field list before recording; when declined, the review SHALL NOT be recorded, and the skill SHALL say so. The skill SHALL set fields and record the review before running any `archive` or `move`, so the record lands in the home note before it moves. A review stopped early SHALL still be recorded, and SHALL add an open `#review` task dated the next workday to finish it.

#### Scenario: Review recorded
- **WHEN** a review of `project/make-bread.md` finishes on 2026-09-25 and the note has no open `#review` task
- **THEN** the note SHALL gain the line `- [x] project #review 📅 ✅ 2026-09-25`

#### Scenario: Scheduled review completed
- **WHEN** the home note has `- [ ] project #review 📅 2026-09-25` and the review finishes that day
- **THEN** that line SHALL be checked off, and no new `#review` line SHALL be added

#### Scenario: Future review kept
- **WHEN** the project was named, its home note has `- [ ] project #review 📅 2026-11-01`, and the review finishes on 2026-09-25
- **THEN** that line SHALL stay open, and the note SHALL gain `- [x] project #review 📅 ✅ 2026-09-25`

#### Scenario: Recorded before archiving
- **WHEN** the user marks `project/make-bread.md` done and confirms archiving it
- **THEN** the status and the completed `#review` line SHALL be written to `project/make-bread.md` before `meta-notes archive` runs

#### Scenario: Folder without a home note
- **WHEN** `project/trip/` has no `Home.md` and the user declines creating one
- **THEN** no `#review` line SHALL be written, and the skill SHALL say the review was not recorded

#### Scenario: Stopped early
- **WHEN** the user stops a review of `project/make-bread.md` on Friday 2026-09-25 before choosing a disposition
- **THEN** the note SHALL gain `- [x] project #review 📅 ✅ 2026-09-25` and `- [ ] Finish project review #review 📅 2026-09-28`
