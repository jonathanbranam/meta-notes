## ADDED Requirements

### Requirement: Project review
`project-review` SHALL review one project per run, in 5–10 minutes, reading its state with `meta-notes project brief`. Its description SHALL NOT trigger on task cleanup. It SHALL NOT propose other projects to review. With no project named, it SHALL pick the project with the oldest last review, preferring never-reviewed projects. It SHALL show the project's files and tasks, open and completed, and give its state in about ten lines. It SHALL ask for a disposition: continue, pause, done, convert to area, split, or merge. Pause and done SHALL set the `status` field; archiving and converting SHALL use `meta-notes archive` or `move`. It SHALL ask for a next action when there is no open `#next`, accepting none as an answer. It SHALL NOT walk through the project's stale tasks one by one; it leaves that to `task-cleanup`. It SHALL record the review as a completed `#review` task in the home note: by checking off an open `#review` task when one exists, or by adding `- [ ] project #review 📅` and checking it off with `task update --status x`. A review stopped early SHALL still be recorded, and SHALL add an open `#review` task dated the next workday to finish it.

#### Scenario: Review recorded
- **WHEN** a review of `project/make-bread.md` finishes on 2026-09-25 and the note has no open `#review` task
- **THEN** the note SHALL gain the line `- [x] project #review 📅 ✅ 2026-09-25`

#### Scenario: Scheduled review completed
- **WHEN** the home note has `- [ ] project #review 📅 2026-09-25` and the review finishes that day
- **THEN** that line SHALL be checked off, and no new `#review` line SHALL be added

#### Scenario: Pause
- **WHEN** the user pauses the project
- **THEN** the home note's `status` field SHALL become `paused`, and the skill SHALL offer to add a dated `#review` task for when to reconsider it

#### Scenario: Oldest review picked
- **WHEN** no project is named and `meta-notes projects` shows one project never reviewed and others reviewed
- **THEN** the skill SHALL review the never-reviewed project without listing the others

#### Scenario: Task cleanup request
- **WHEN** the user asks the agent to clean up stale tasks
- **THEN** `project-review` SHALL NOT match the request
