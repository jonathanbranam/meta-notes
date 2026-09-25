# project-brief Specification

## Purpose

Specifies `meta-notes project brief`, which returns one project's fields, files, tasks, and dates in a single call, so a project review or the dashboard sees the project's full state without running several queries.

## Requirements

### Requirement: Project argument
`meta-notes project brief <path>` SHALL accept a project as defined by `project-fields`: a note directly in `project/` or `archive/project/`, given with or without `.md`, or a folder directly in one of them, given with or without a trailing `/`. `<path>` SHALL be relative to the notes root, or an absolute path inside it. Any other path, including an area, a note nested inside a folder project, or a path that doesn't exist, SHALL fail with an error naming the path. The command SHALL NOT write any file.

#### Scenario: Note project without extension
- **WHEN** the notes root has `project/make-bread.md` and the user runs `meta-notes project brief project/make-bread`
- **THEN** the brief SHALL be for `project/make-bread.md`

#### Scenario: Folder project
- **WHEN** the notes root has `project/kitchen/Home.md` and the user runs `meta-notes project brief project/kitchen/`
- **THEN** the brief SHALL be for `project/kitchen/`, with home note `project/kitchen/Home.md`

#### Scenario: Area rejected
- **WHEN** the user runs `meta-notes project brief area/health`
- **THEN** the command SHALL exit non-zero with an error saying `area/health` is not a project

#### Scenario: Nested note rejected
- **WHEN** the user runs `meta-notes project brief project/kitchen/Tasks.md`
- **THEN** the command SHALL exit non-zero with an error saying it is not a project

### Requirement: Home note and fields
The brief SHALL report the project's path, its home note (or none), all its fields as read by `project-fields`, its `status` (`active` when the field is missing), and its `tag` (none when the field is missing). A folder project with no `Home.md` SHALL still be briefed, with no home note, default fields, and a `no-home-note` warning.

#### Scenario: Fields reported
- **WHEN** `project/make-bread.md` is `# Make Bread`, a blank line, `- status: paused`, `- tag: make-bread`
- **THEN** the brief SHALL have status `paused`, tag `make-bread`, and home note `project/make-bread.md`

#### Scenario: Folder without a home note
- **WHEN** `project/trip/` has `Packing.md` and no `Home.md`
- **THEN** the brief SHALL have no home note, status `active`, no tag, and a `no-home-note` warning

### Requirement: Project files
The brief SHALL list every file in the project's note or folder, including files in subfolders and files that aren't markdown, except files and folders whose names start with `.`. Each file SHALL have its path relative to the notes root, its size in bytes, and its modification date as `YYYY-MM-DD` in local time. Files SHALL be sorted by path. Modification dates SHALL NOT be used for the latest date or any other date in the brief.

#### Scenario: Folder files
- **WHEN** `project/kitchen/` has `Home.md`, `meetings/2026-09-18.md`, and `plan.pdf`
- **THEN** the brief SHALL list all three, each with its size and modification date

#### Scenario: Note project
- **WHEN** the brief is for `project/make-bread.md`
- **THEN** the file list SHALL be that one note

#### Scenario: Recent modification doesn't count as activity
- **WHEN** today is 2026-09-25, a project file was modified today by a link rewrite, and the project's latest date by the `project-list` rule is 2026-03-02
- **THEN** the brief's latest date SHALL be 2026-03-02

### Requirement: Project tasks
The brief's tasks SHALL be the project's tasks as `project-list` defines them: every task in the project's note or folder, plus every task anywhere in the notes root that carries the project's tag, each counted once. A task is a line that `meta-notes tasks` treats as a task; checkbox lines without a date marker SHALL NOT be reported. The brief SHALL report open tasks (status `incomplete`) and completed tasks (status `completed`); canceled and rescheduled tasks SHALL NOT be listed. Tasks SHALL be sorted by file path, then line number.

#### Scenario: Tagged task elsewhere
- **WHEN** `project/make-bread.md` has tag `make-bread` and `plan/daily/26-Q3/2026-09-24.md` has `- [ ] #make-bread buy flour 📅 2026-09-26`
- **THEN** that task SHALL be among the brief's open tasks

#### Scenario: Plain checkbox ignored
- **WHEN** the project's home note has `- [ ] buy a banneton` with no date marker
- **THEN** the line SHALL NOT appear in the brief

#### Scenario: Canceled task left out
- **WHEN** the project has `- [-] rent a mixer 📅 2026-08-01`
- **THEN** the task SHALL NOT appear in the brief

### Requirement: Open task lists
Every open task SHALL be listed. Open tasks tagged `#later` SHALL be listed separately from the other open tasks and not among them. In addition, the brief SHALL list the open tasks tagged `#deadline`, and the open tasks tagged `#review` that have a due date, each with its due date; these tasks SHALL also appear in the open task list. `has_next` SHALL be true when an open task is tagged `#next`, the same test `project-list` uses for `no-next`. When the project is `active` and `has_next` is false, the brief SHALL carry a `no-next` warning; the command SHALL still succeed.

#### Scenario: Later listed separately
- **WHEN** the project has `- [ ] #later try rye 📅` and `- [ ] buy flour 📅 2026-09-26`
- **THEN** `try rye` SHALL be in the later list only, and `buy flour` in the open list

#### Scenario: Deadline and scheduled review
- **WHEN** the project has `- [ ] Bake for the party #deadline 📅 2026-10-30` and `- [ ] project #review 📅 2026-11-01`
- **THEN** the brief SHALL list the first as a deadline due 2026-10-30 and the second as a scheduled review due 2026-11-01, and both SHALL be in the open list

#### Scenario: Unscheduled review not listed as scheduled
- **WHEN** the project's only open `#review` task is `- [ ] project #review 📅`
- **THEN** the scheduled review list SHALL be empty

#### Scenario: No next action
- **WHEN** an `active` project has open tasks but none tagged `#next`
- **THEN** `has_next` SHALL be false, the brief SHALL have a `no-next` warning, and the command SHALL exit zero

### Requirement: Completed task window
A completed task's completion date SHALL be its ✅ date, or its due date when it has none. Completed tasks SHALL be listed when their completion date is on or after the start of the window: today minus 90 days, or the `--since` date when given. Completed tasks without a completion date SHALL NOT be listed. The brief SHALL always report the total number of the project's completed tasks, including those not listed. `--since` SHALL take a `YYYY-MM-DD` date; any other value SHALL fail with a usage error.

#### Scenario: Default window
- **WHEN** today is 2026-09-25 and the project has tasks completed on 2026-07-01 and 2026-05-01
- **THEN** only the task completed on 2026-07-01 SHALL be listed, and the completed total SHALL be 2

#### Scenario: Since
- **WHEN** the same project is briefed with `--since 2026-01-01`
- **THEN** both completed tasks SHALL be listed

#### Scenario: Due date stands in
- **WHEN** today is 2026-09-25 and the project has `- [x] order flour 📅 2026-09-20`
- **THEN** the task SHALL be listed with completion date 2026-09-20

#### Scenario: Invalid since
- **WHEN** the user runs `meta-notes project brief project/make-bread --since 2026-09`
- **THEN** the command SHALL exit non-zero with a usage error

### Requirement: Project dates and warnings
The brief SHALL report the project's latest date and last review, as `project-list` defines them, or none. It SHALL carry the warnings `project-list` defines for a project (`no-next`, `no-recent-activity`, `review-overdue`), plus `no-home-note`, under the same rules, so the brief and `meta-notes projects` agree for any project. Warnings SHALL NOT make the command fail.

#### Scenario: Same answers as the project list
- **WHEN** `meta-notes projects --json` lists `project/make-bread.md` with a latest date, last review, and warnings
- **THEN** `meta-notes project brief project/make-bread --json` SHALL report the same latest date, last review, and warnings

#### Scenario: Review doesn't count as activity
- **WHEN** today is 2026-09-25, the project's only heading date is `## Notes 2026-04-01`, and its home note has `- [x] project #review 📅 ✅ 2026-09-20`
- **THEN** the brief SHALL have latest date 2026-04-01 and last review 2026-09-20

### Requirement: Brief output
The text output SHALL start with the project's path, status, tag, latest date, and last review (or `never`), then its warnings, then sections for files, deadlines, scheduled reviews, open tasks, later tasks, and completed tasks, with the completed section's heading giving the number listed and the total. Empty sections SHALL be left out. With `--json`, the result SHALL have a `project` object, alongside the CLI's `ok` and `warnings` (which keep their meaning from `cli`), with `path`, `home` (or null), `status`, `tag` (or null), `fields` (an object of every field, keys lowercase), `latest_date` (or null), `last_review` (or null), `has_next`, `warnings` (a list of names), `files` (each with `path`, `size`, and `modified`), `open`, `later`, `deadlines`, `scheduled_reviews`, `completed`, `completed_total`, and `since` (the start of the completed window). Each task SHALL have the fields a `meta-notes tasks --json` task has, except `section`.

#### Scenario: JSON result
- **WHEN** today is 2026-09-25, `project/make-bread.md` has tag `make-bread`, one open `#next` task, and was never reviewed, and the user runs `meta-notes project brief project/make-bread --json`
- **THEN** the result's `project` object SHALL have `tag` `make-bread`, `has_next` true, `last_review` null, `since` `2026-06-27`, `review-overdue` in `warnings`, and the `#next` task in `open` with its file, line, and text

#### Scenario: Task line usable by task update
- **WHEN** the brief's JSON lists a task with file `project/make-bread.md`, line 5, and text `- [ ] buy flour 📅 2026-09-26`
- **THEN** `meta-notes task update project/make-bread.md:5 --expect '- [ ] buy flour 📅 2026-09-26' --status x` SHALL find the line
