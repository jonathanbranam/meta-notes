## MODIFIED Requirements

### Requirement: Shipped skills
The plugin SHALL ship `daily-shutdown`, `daily-plan`, `weekly-review`, `weekly-plan`, `task-cleanup`, and `project-review` as `skills/<name>/SKILL.md`, installed into a notes root by `meta-notes init`. Each skill's description SHALL name when to use it, and SHALL NOT trigger on another skill's ceremony.

#### Scenario: Skills installed
- **WHEN** the user runs `meta-notes init` in a notes root
- **THEN** `.claude/skills/` SHALL contain all six skills

#### Scenario: Task cleanup request
- **WHEN** the user asks the agent to clean up stale tasks
- **THEN** the `task-cleanup` skill SHALL match the request

## ADDED Requirements

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
