## Purpose

Specifies `meta-notes projects`, which lists every project with its status, last review, and warnings derived from its tasks, so the weekly review can flag stalled or unreviewed projects without opening each one.

## ADDED Requirements

### Requirement: Projects listed
`meta-notes projects` SHALL list each project under `project/`: each `.md` note directly in `project/`, and each folder directly in `project/`. A folder project's home note SHALL be its `Home.md`; a note project's home note SHALL be the note itself. A folder with no `Home.md` SHALL still be listed, with a `no-home-note` warning and default fields. Projects under `archive/` SHALL NOT be listed. Projects SHALL be sorted by path. The command SHALL NOT write any file.

#### Scenario: Note and folder projects
- **WHEN** the notes root has `project/make-bread.md` and `project/kitchen/Home.md`
- **THEN** both SHALL be listed, as `project/make-bread.md` and `project/kitchen/`

#### Scenario: Folder without a home note
- **WHEN** `project/trip/` has notes but no `Home.md`
- **THEN** `project/trip/` SHALL be listed with a `no-home-note` warning

### Requirement: Project fields
A project's fields SHALL be the `key: value` items of the first list after the home note's first heading, when that list comes before any other heading. `status` SHALL be `active` when missing. A project with no `tag` field SHALL have no tag. Field keys SHALL be compared ignoring case. Frontmatter SHALL NOT be read.

#### Scenario: Fields read
- **WHEN** a home note is `# Make Bread`, a blank line, `- status: paused`, `- tag: make-bread`
- **THEN** the project's status SHALL be `paused` and its tag `make-bread`

#### Scenario: No fields
- **WHEN** a home note has a title and no list after it
- **THEN** the project's status SHALL be `active` and it SHALL have no tag

### Requirement: Project tasks
A project's tasks SHALL be every task in its note or folder, plus every task anywhere in the notes root that carries the project's tag (matched the way task queries match tags), open and completed, counted once each. A task is a line that `meta-notes tasks` treats as a task.

#### Scenario: Tagged task elsewhere
- **WHEN** project `project/make-bread.md` has tag `make-bread` and a daily note has `- [ ] #make-bread buy flour 📅 2026-09-26`
- **THEN** that task SHALL be one of the project's tasks

#### Scenario: Untagged project
- **WHEN** a project has no tag
- **THEN** its tasks SHALL be only those in its note or folder

### Requirement: Latest date
A project's latest date SHALL be the latest valid `YYYY-MM-DD` date, on or before today, that appears in the name of a file in its note or folder, in a markdown heading line in one of those files, or in the text of one of the project's tasks. Tasks tagged `#review` SHALL NOT count, so recording a review does not make a project look active. Dates elsewhere in a file's contents, including the field list, SHALL NOT count. Dates after today SHALL NOT count. A project with no such date SHALL have no latest date. Git history and file modification times SHALL NOT be used.

#### Scenario: Dated meeting note
- **WHEN** today is 2026-09-25 and `project/kitchen/` has `Home.md` and `meetings/2026-09-18.md`, and no later date appears in the project
- **THEN** the project's latest date SHALL be 2026-09-18

#### Scenario: Future due date ignored
- **WHEN** today is 2026-09-25 and a project's only dates are a `## Notes 2026-03-02` heading and a task due 2026-12-01
- **THEN** the project's latest date SHALL be 2026-03-02

#### Scenario: Dated heading
- **WHEN** today is 2026-09-25 and `project/make-bread.md` has a `## Notes 2026-09-10` heading and no later date in its file name, headings, or tasks
- **THEN** the project's latest date SHALL be 2026-09-10

#### Scenario: Body text and reviews ignored
- **WHEN** today is 2026-09-25, a project's only heading date is `## Notes 2026-04-01`, a paragraph in its home note mentions 2026-09-01, and its home note has `- [x] project #review 📅 ✅ 2026-09-20`
- **THEN** the project's latest date SHALL be 2026-04-01

#### Scenario: Tagged task elsewhere counts
- **WHEN** a project has tag `make-bread`, its own files' latest date is 2026-05-01, and a daily note has `- [x] #make-bread order flour 📅 2026-09-20`
- **THEN** the project's latest date SHALL be 2026-09-20

### Requirement: Last review
A project's last review SHALL be the latest completion date among its completed tasks tagged `#review` (the ✅ date, or the due date for a completed task without one). A project with no completed `#review` task SHALL have never been reviewed.

#### Scenario: Latest review wins
- **WHEN** a project has `- [x] project #review 📅 ✅ 2026-06-01` and `- [x] project #review 📅 ✅ 2026-09-03`
- **THEN** its last review SHALL be 2026-09-03

#### Scenario: Scheduled review not yet done
- **WHEN** a project's only `#review` task is `- [ ] project #review 📅 2026-11-01`
- **THEN** it SHALL have never been reviewed

### Requirement: Project warnings
Each project SHALL carry these warnings when they apply, with today as the reference date and a threshold of 30 days:

- `no-next`: the project is `active` and none of its open tasks is tagged `#next`
- `no-recent-activity`: the project is `active` and its latest date is more than 30 days before today, or it has none
- `review-overdue`: the project's status is not `done` and its last review is more than 30 days before today, or it has never been reviewed

Warnings SHALL NOT make the command fail.

#### Scenario: Paused project
- **WHEN** a `paused` project has no `#next` task and no recent activity, and was reviewed 10 days ago
- **THEN** it SHALL have no warnings

#### Scenario: Stalled active project
- **WHEN** today is 2026-09-25 and an `active` project's latest date is 2026-08-01, with no open `#next`, and it was last reviewed on 2026-07-15
- **THEN** it SHALL have `no-next`, `no-recent-activity`, and `review-overdue` warnings

### Requirement: Project list output
The text output SHALL be one line per project with its path, status, latest date, last review date (or `never`), and warnings. `--warnings` SHALL list only projects with at least one warning. With `--json`, the result SHALL have a `projects` list, each entry with `path`, `home` (the home note path, or null), `status`, `tag` (or null), `last_review` (a date or null), `latest_date` (a date or null), `open_tasks`, `completed_tasks`, and `warnings` (a list of the names above).

#### Scenario: Only warnings
- **WHEN** the user runs `meta-notes projects --warnings`
- **THEN** projects with no warnings SHALL be left out

#### Scenario: JSON result
- **WHEN** the user runs `meta-notes projects --json` and `project/make-bread.md` has tag `make-bread` and was never reviewed
- **THEN** its entry SHALL have `tag` `make-bread`, `last_review` null, and `review-overdue` in `warnings`
