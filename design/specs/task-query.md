## Purpose

Specifies `meta-notes tasks`, the CLI task query that exposes the existing `scripts/find_tasks.py` filters and output unchanged, adds `--json` output, and keeps the standalone script working for templates.

## Requirements

### Requirement: Task query matches find_tasks  {#r-1251}
`meta-notes tasks` SHALL accept the same options as `scripts/find_tasks.py`: `--date`, `--scheduled`, `--due`, `--overdue`, `--ready`, `--future`, `--undated`, `--all`, `--later`, `--tag`, `--group-by`, `--folder`, `--status`, `--format`, and `--condensed`. For the same options and notes root, it SHALL print the same output that `find_tasks.py` prints.

#### Scenario: Default report  {#s-bebb}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks` with no options
- **THEN** the output SHALL equal `python3 scripts/find_tasks.py` run in the notes root

#### Scenario: Filtered query  {#s-b270}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --folder project --status all --all`
- **THEN** the output SHALL equal `find_tasks.py --folder project --status all --all` run in the notes root

### Requirement: Task query JSON  {#r-8297}
With `--json`, `meta-notes tasks` SHALL return the same tasks as the text output, in the same order. Each task SHALL have its file, line number, line text, status, start, due, and completed dates, `time` (the time of day as 24-hour `HH:MM`, or null), `recurrence` (the rule text as written, or null), `recurs_from_completion` (true for a `when done` rule), `tags` (canonical names without `#`), `section` (the section it is listed in: `overdue`, `due`, `scheduled`, `ready`, `future`, or `undated`), and its `notes`, `parent` and `subtasks` (see the `task-tree` spec). A task listed under several tags with `--group-by tag` SHALL appear once.

#### Scenario: JSON task fields  {#s-e78e}
*Verification*: **non-executable**
- **WHEN** `project/foo.md` line 3 is `- [ ] #mtg Call Sam 📅 2026-10-01` and the user runs `meta-notes tasks --folder project --all --json`
- **THEN** the result SHALL include a task with file `project/foo.md`, line 3, status `incomplete`, due date `2026-10-01`, and tags `["meeting"]`

#### Scenario: JSON section  {#s-54145}
*Verification*: **non-executable**
- **WHEN** a task is due 2026-09-20 and the user runs `meta-notes tasks --overdue --ready --date 2026-09-25 --json`
- **THEN** the task SHALL appear once with section `overdue`

### Requirement: A task needs a date marker  {#r-21a1}
A checkbox line (`-`, `*`, or `+`, then `[<char>]`) SHALL be a task only when it contains a due-date emoji (📅, 📆, or 🗓), with or without a date after it, or `🛫` followed by a `YYYY-MM-DD` date. Other checkbox lines SHALL be ignored by every mode. The date after 📅, 📆, or 🗓 SHALL be the task's due date. A due-date emoji with no valid date after it SHALL mark the task undated.

#### Scenario: Plain checkbox ignored  {#s-298a}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] buy milk` and the user runs `meta-notes tasks --all`
- **THEN** the line SHALL NOT be listed

#### Scenario: Each due emoji recognized  {#s-f6de}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] a 📅 2026-10-01`, `- [ ] b 📆 2026-10-01`, and `- [ ] c 🗓 2026-10-01`
- **THEN** all three SHALL be tasks due 2026-10-01

#### Scenario: Bare due emoji  {#s-51bd}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] someday task 📅`
- **THEN** it SHALL be an undated task

#### Scenario: Start date only  {#s-3f01}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] draft outline 🛫 2026-10-05`
- **THEN** it SHALL be a task with start date 2026-10-05 and no due date

### Requirement: Time of day  {#r-02aa}
A task's time of day SHALL be read from a `⏰` marker, `⏰ HH:MM` (24-hour) or the Time Block's 12-hour style such as `⏰ 3:15pm`, or from a 24-hour time after the due date, `📅 YYYY-MM-DD HH:MM`. When a line has both, the `⏰` time SHALL be used. A `📅` date followed by a time SHALL still be that due date in every mode. `⏰` and a time SHALL NOT make a line a task, and a time SHALL NOT change which section a task is listed in: a task is due today by its date, timed or not.

A `⏰` with no valid time after it SHALL be ignored and reported as a warning. A time on a task with no valid due date (none, bare due emoji, or only `🛫`) SHALL be ignored and reported as a warning.

#### Scenario: Both forms  {#s-4014}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] a ⏰ 3:15pm 📅 2026-10-01` and `- [ ] b 📅 2026-10-01 08:30`
- **THEN** `meta-notes tasks --all --json` SHALL report `time` `15:15` for a and `08:30` for b, both due 2026-10-01

#### Scenario: Due today ignores the time  {#s-d713}
*Verification*: **non-executable**
- **WHEN** a task is due 2026-09-25 at 23:59, another at 00:01, and another has no time, and the user runs `meta-notes tasks --due --date 2026-09-25`
- **THEN** all three SHALL be listed as due

#### Scenario: Time without a due date  {#s-a482}
*Verification*: **non-executable**
- **WHEN** a task is `- [ ] call ⏰ 15:00 🛫 2026-10-01` and the user runs `meta-notes tasks --all --json`
- **THEN** its `time` SHALL be null or ignored, and `warnings` SHALL say the time has no due date

### Requirement: Recurrence on tasks  {#r-51c4}
A task's recurrence SHALL be read from a `🔁` marker (optionally followed by the emoji variation selector) and the rule text after it, which runs to the next `📅 📆 🗓 🛫 ✅ ⏰` marker, the first `#tag`, or the end of the line. A supported rule (see the `recurrence` spec) SHALL be reported as `recurrence`, the rule text as written, and `recurs_from_completion`, true when the rule ends in `when done`; a task without a rule SHALL have `recurrence` null and `recurs_from_completion` false. `🔁` SHALL NOT make a line a task. A valid rule on a task with no valid due or start date SHALL NOT be recurring unless it is `when done`. A `🔁` whose text is not a supported rule SHALL be ignored and reported as a warning, and the query SHALL NOT fail.

#### Scenario: Recurrence fields  {#s-3a9e}
*Verification*: **non-executable**
- **WHEN** a note contains `- [ ] change filter 🔁 every 3 months 📅 2026-07-01 #home` and `- [ ] salt 🔁 every month when done 📅 2026-07-24`, and the user runs `meta-notes tasks --all --json`
- **THEN** the first task SHALL have `recurrence` `every 3 months` and `recurs_from_completion` false, and the second `every month when done` and true

#### Scenario: Unsupported rule  {#s-c8d2}
*Verification*: **non-executable**
- **WHEN** a task is `- [ ] sweep 🔁 every other week 📅 2026-10-01` and the user runs `meta-notes tasks --all --json`
- **THEN** its `recurrence` SHALL be null, the task SHALL still be listed, and `warnings` SHALL name the line's unsupported rule

### Requirement: Completion date stands in for the due date  {#r-ebb9}
For a completed task that has a `✅ YYYY-MM-DD` date, that date SHALL be used in place of its due date by every mode. A completed task without a ✅ date SHALL use its due date.

#### Scenario: Completed with a completion date  {#s-3cab}
*Verification*: **non-executable**
- **WHEN** a note contains `- [x] ship it 📅 2026-10-01 ✅ 2026-10-03` and the user runs `meta-notes tasks --status completed --due --date 2026-10-03`
- **THEN** the task SHALL be listed

#### Scenario: Completed without a completion date  {#s-9e6b}
*Verification*: **non-executable**
- **WHEN** a note contains `- [x] ship it 📅 2026-10-01` and the user runs `meta-notes tasks --status completed --due --date 2026-10`
- **THEN** the task SHALL be listed

### Requirement: Task tags  {#r-b97c}
Every `#tag` on a task line SHALL be a tag of the task, wherever it appears in the line. A tag is `#` followed by letters, digits, `_`, or `-`. The tags `#mtg`, `#pers`, `#per`, and `#waiting` SHALL be read as `meeting`, `personal`, `personal`, and `wait`, the same aliases that time log entries use. Tags SHALL be compared ignoring case.

#### Scenario: Several tags  {#s-6e23}
*Verification*: **non-executable**
- **WHEN** a task line is `- [ ] #aftr #design follow up 📅 2026-07-08`
- **THEN** its tags SHALL be `aftr` and `design`

#### Scenario: Alias  {#s-b2c8}
*Verification*: **non-executable**
- **WHEN** a task line is `- [ ] #mtg prep 📅 2026-10-01`
- **THEN** its tags SHALL be `meeting`, and `--tag mtg` and `--tag meeting` SHALL both select it

#### Scenario: Waiting alias  {#s-fbff}
*Verification*: **non-executable**
- **WHEN** a task line is `- [ ] #waiting legal sign-off 📅 2026-10-15`
- **THEN** its tags SHALL be `wait`, and `--tag wait` and `--tag waiting` SHALL both select it

### Requirement: Selection modes  {#r-4720}
The period from `--date` (see `date-period`) SHALL set START and END. Tasks SHALL first be filtered by `--status` (default `incomplete`), `--folder`, and `--tag`. The modes SHALL then select:

| Mode | Selects tasks whose |
|---|---|
| `--overdue` | due date is before START |
| `--due` | due date is within START..END |
| `--scheduled` | due date or start date is within START..END |
| `--ready` | due date or start date is on or before END |
| `--future` | due or start date exists, and neither is on or before END |
| `--undated` | due-date emoji is bare, with no start date |

`--all` SHALL select `--ready`, `--future`, and `--undated` together. With no mode, `--ready` SHALL be used. Modes SHALL combine. Each selected task SHALL be listed once, in the first matching selected mode in the order overdue, due, scheduled, ready, future, undated.

#### Scenario: Default is ready as of today  {#s-b6da}
*Verification*: **non-executable**
- **WHEN** today is 2026-09-25, task A is due 2026-09-20, task B starts 2026-09-25 and is due 2026-10-30, and task C is due 2026-10-01, and the user runs `meta-notes tasks`
- **THEN** A and B SHALL be listed and C SHALL NOT

#### Scenario: Ready by Sunday  {#s-0188}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --ready --date 2026-09-27` and task C is due 2026-09-26
- **THEN** C SHALL be listed

#### Scenario: Overdue  {#s-0c66}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --overdue --date 2026-09-25`, task A is due 2026-09-24, task D is due 2026-09-25, and task E starts 2026-09-01 with no due date
- **THEN** only A SHALL be listed

#### Scenario: Due today ignores start dates  {#s-a441}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --due --date 2026-09-25`, task D is due 2026-09-25, and task F starts 2026-09-25 and is due 2026-10-10
- **THEN** only D SHALL be listed

#### Scenario: Scheduled in a month  {#s-d7e7}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --scheduled --date 2026-11` with tasks due 2026-10-15, due 2026-11-12, starting 2026-11-03, and starting 2026-10-01 and due 2026-12-15
- **THEN** only the task due 2026-11-12 and the task starting 2026-11-03 SHALL be listed

#### Scenario: Future and undated  {#s-6499}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --future --undated --date 2026-09-25`, task C is due 2026-10-01, and task U is `- [ ] someday 📅`
- **THEN** C SHALL be listed in the future section and U in the undated section

#### Scenario: All  {#s-e875}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --all`
- **THEN** every task with the selected status, except `#later` tasks, SHALL be listed

### Requirement: Query at a time of day  {#r-6f7b}
`meta-notes tasks` SHALL accept `--at TIME`, where TIME is `now` or a 24-hour `HH:MM`, and `--date` SHALL then name a single day (default today); a longer period or an invalid TIME SHALL be a usage error. `now` SHALL be the current time in the machine's local time zone (never UTC). On that day, a timed task due earlier than TIME SHALL be overdue, one due at TIME SHALL be due, and one due later SHALL be future and not due or ready; a task with no time SHALL be due all day, as without `--at`. Completed tasks SHALL ignore their time. `--at` SHALL NOT change `--scheduled`, `--undated`, or tasks due on other days, and without `--at` the time SHALL NOT affect selection.

#### Scenario: Split by time  {#s-d373}
*Verification*: **non-executable**
- **WHEN** tasks are due 2026-09-25 at 09:00, at 12:00, at 15:15, and with no time, and the user runs `meta-notes tasks --overdue --due --future --date 2026-09-25 --at 12:00`
- **THEN** the 09:00 task SHALL be overdue, the 12:00 and untimed tasks due, and the 15:15 task future

#### Scenario: Ready excludes later today  {#s-fb36}
*Verification*: **non-executable**
- **WHEN** the same tasks exist and the user runs `meta-notes tasks --ready --date 2026-09-25 --at 12:00`
- **THEN** the 15:15 task SHALL NOT be listed

#### Scenario: Period rejected  {#s-dfac}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --date 2026-09 --at now`
- **THEN** the command SHALL fail saying `--at` needs a single day

### Requirement: Later tasks are excluded unless requested  {#r-fdff}
A task tagged `#later` (any case) SHALL NOT be selected by any mode unless `--later` is given. With `--later`, `#later` tasks SHALL be selected by the same rules as other tasks and listed in the same sections.

#### Scenario: Later excluded  {#s-b084}
*Verification*: **non-executable**
- **WHEN** a task is `- [ ] #later read book 📅 2026-09-01` and the user runs `meta-notes tasks --overdue`
- **THEN** it SHALL NOT be listed

#### Scenario: Later included  {#s-0ea5}
*Verification*: **non-executable**
- **WHEN** the same task exists and the user runs `meta-notes tasks --overdue --later` on 2026-09-25
- **THEN** it SHALL be listed in the overdue section

### Requirement: Daily snapshot sections are not tasks  {#r-a474}
Task scanning SHALL ignore checkbox lines under the `## Tasks Due Today` and `## Overdue Tasks` headings of a note under `plan/daily/`, up to the next `##` heading. Tasks elsewhere in a daily note SHALL still count. This applies to every command that scans tasks, including the blocks a new daily note renders.

#### Scenario: Copies are skipped  {#s-6914}
*Verification*: **non-executable**
- **WHEN** a daily note has a task under `## Tasks Due Today`, one under `## Overdue Tasks` and one under `## Notes`, and the user runs `meta-notes tasks --due --overdue`
- **THEN** only the `## Notes` task SHALL be listed for that note

### Requirement: Report layout  {#r-6ee3}
Tasks SHALL be grouped by file, files sorted by path, and tasks in file order. Each task SHALL be printed as its original line, including its bullet, checkbox, and indentation. In standard format each file SHALL start with a `## [[<link>]]` heading, and in condensed format with a `- [[<link>]]` item and the task lines indented two spaces. When more than one mode is selected, each non-empty section SHALL start with a heading: `# Overdue`, `# Due`, `# Scheduled`, `# Ready`, `# Future`, or `# Undated`. With a single mode, there SHALL be no section heading. Standard format SHALL end with a summary line giving the number of tasks and files.

#### Scenario: Single mode has no section heading  {#s-cde4}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --due --condensed` and one task in `project/foo.md` is due today
- **THEN** the output SHALL be `- [[project/foo]]` followed by the indented task line

#### Scenario: Several modes have section headings  {#s-d337}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --overdue --due` and both sections have tasks
- **THEN** the output SHALL contain `# Overdue` before `# Due`

### Requirement: Group by tag  {#r-2670}
With `--group-by tag`, each section SHALL list its tasks under a `## <tag>` heading for each tag, sorted ignoring case, followed by `## Not tagged` for tasks without tags. A task with several tags SHALL be listed under each. Under a tag heading, standard-format file headings SHALL be `### [[<link>]]`.

#### Scenario: Tag headings  {#s-d8a3}
*Verification*: **non-executable**
- **WHEN** ready tasks are tagged `#cd`, `#Admin`, and none, and the user runs `meta-notes tasks --group-by tag`
- **THEN** the headings SHALL appear in the order `## Admin`, `## cd`, `## Not tagged`

#### Scenario: Tag filter with grouping  {#s-3662}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes tasks --group-by tag --tag admin --tag cd`
- **THEN** only tasks tagged `admin` or `cd` SHALL be listed, under their tag headings

### Requirement: Removed date options are rejected  {#r-ae7d}
`--due-on`, `--due-by`, and `--due-between` SHALL NOT be accepted. Using one SHALL be a usage error that exits non-zero.

#### Scenario: Old option  {#s-1bf5}
*Verification*: **non-executable**
- **WHEN** the user runs `find_tasks.py --due-on 2026-09-25`
- **THEN** it SHALL exit non-zero with a usage error on stderr
