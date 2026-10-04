# agent-prime Specification

## Purpose
Specifies `meta-notes prime`, which prints a guide to a notes root for an agent to read at the start of a session: the folder structure, the kinds of notes and where they live, projects and the archive, the commands for finding things, and the conventions, so the guide ships with the plugin and always matches it.

## Requirements

### Requirement: Prime command  {#r-51db}
`meta-notes prime` SHALL print the guide as markdown to stdout. With `--json`, the result SHALL have `version` (the CLI version), `root` (the absolute notes root, or null), `mode` (the root's mode), and `text` (the same markdown). Near the top, the guide SHALL state the root's mode. The command SHALL NOT write any file.

#### Scenario: Inside a notes root  {#s-48c1}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime` in `project/kitchen/` of a notes root
- **THEN** the command SHALL succeed and print the guide

#### Scenario: JSON result  {#s-1ad0}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime --json` in a notes root
- **THEN** the result SHALL have `ok` true, `version`, `root` set to the notes root, and `text`

### Requirement: Prime works outside a notes root  {#r-dba3}
When no notes root is found, `meta-notes prime` SHALL still succeed, SHALL print the guide, and SHALL begin the guide with a line saying no notes root was found and that `meta-notes init` creates one. With `--json`, `root` SHALL be null.

#### Scenario: No notes root  {#s-72fc}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime --json` in a directory with no `.meta-notes` above it
- **THEN** the result SHALL have `ok` true and `root` null, and `text` SHALL mention `meta-notes init`

### Requirement: Prime content  {#r-0e11}
The guide SHALL cover:

- the folders `plan/`, `project/`, `area/`, `resource/`, and `archive/` and what belongs in each; `resource/template/` as the home of the templates
- naming: folders lowercase with dashes instead of spaces; note names in Title Case with spaces, ending in `.md`; plan notes named by date; other file types allowed beside notes
- plan notes: the paths of today's daily, weekly, quarterly, and yearly notes, what `YY-QN` means, and `meta-notes note` to create one; the guide SHALL NOT list the sections of plan notes
- projects: a single note or a folder with `Home.md`; the common project files `Tasks.md` and `Meetings & Notes.md`, the latter with dated headings, newest first; the `status`, `tag`, and `archived` fields; `#next`, `#review`, and `#deadline`; `meta-notes projects` as the list of projects and `meta-notes project brief` for one project; converting a project to an area with `meta-notes move`
- areas as ongoing responsibilities that may hold or link to projects and resources; resources as reference material, including notes from general meetings
- the archive: archiving moves an item to `archive/<original path>`, sets `status: archived` and `archived: <date>` on a project, keeps links resolving, and is done only with `meta-notes archive`; archived items stay searchable
- the working day, by the root's mode, read from the same source as `conventions` and `checkin`: in `work` mode 08:00 to 17:00, Monday to Friday, with no work planned after 17:00, and the time block running to 18:00 so after-work personal events can go in it; in `personal` mode 07:00 to 21:00, every day of the week, with no work cutoff
- the daily note's time log (an entry bullet naming the activity, with tags, and `start:` and `end:` sub-bullets, times given only as `HH:MM`) and time block table
- the commands for finding things: `tasks`, `projects`, `project brief`, `changes`, `calendar`, `ceremony status`, and `time`, as one example command line each
- the shipped skills, by name
- that the user's personal preferences, such as working hours and routines, are in the notes root's `CLAUDE.md` and override the guide's defaults
- the full conventions, identical to the output of `meta-notes conventions`

#### Scenario: Conventions included  {#s-759c}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime`
- **THEN** the output SHALL contain the output of `meta-notes conventions`

#### Scenario: Working hours stated  {#s-1786}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime`
- **THEN** the output SHALL give the working day as 08:00 to 17:00, Monday to Friday

#### Scenario: Personal hours stated  {#s-9711}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime` in a root whose mode is `personal`
- **THEN** the output SHALL give the day as 07:00 to 21:00, every day of the week, and SHALL NOT say to stop planning work at 17:00

#### Scenario: Archive rule present  {#s-13f3}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime`
- **THEN** the output SHALL say that archiving is done only with `meta-notes archive` and that archived items keep their path under `archive/`

### Requirement: Generated parts  {#r-f718}
These parts of the guide SHALL be generated, not written by hand, so they match the installed CLI and the notes root:

- today's daily, weekly, quarterly, and yearly note paths, computed as `meta-notes note` computes them, using today's date
- the time report's tag groups and the tags in each
- the names of the skills the plugin ships

#### Scenario: Today's daily path  {#s-2446}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime` on 2026-09-26
- **THEN** the output SHALL contain `plan/daily/26-Q3/2026-09-26 Sat.md` and `plan/week/26-Q3/2026-09-21.md`

#### Scenario: New skill listed  {#s-b565}
*Verification*: **non-executable**
- **WHEN** the plugin ships `skills/calendar/`
- **THEN** the guide SHALL list `calendar`

### Requirement: Prime output size  {#r-1d0e}
The guide, including the conventions, SHALL be at most 10,000 characters, so it costs little context in every session. It SHALL contain no markdown tables.

#### Scenario: Size budget  {#s-b0f8}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes prime` in a notes root
- **THEN** stdout SHALL be at most 10,000 characters and no line SHALL start with `|`
