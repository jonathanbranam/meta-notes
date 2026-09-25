## Purpose

Specifies the `meta-notes note` commands, which create daily, weekly,
quarterly, yearly, and other notes from templates, so Vim, agents, and other
tools create notes the same way. It covers note paths, never overwriting,
`--render`, JSON output, and how Vim uses the commands.

## ADDED Requirements

### Requirement: Periodic note paths
`meta-notes note daily|weekly|quarterly|yearly [<date>]` SHALL compute the
note's path from `<date>`, which defaults to today and SHALL be given as
`YYYY-MM-DD`. Paths SHALL be relative to the notes root:

| Kind | Path | Template date |
|---|---|---|
| `daily` | `plan/daily/YY-QN/YYYY-MM-DD ddd.md` | the date |
| `weekly` | `plan/week/YY-QN/YYYY-MM-DD.md`, dated the Monday of the date's week | that Monday |
| `quarterly` | `plan/quarter/YYYY-QN.md` | first day of the quarter |
| `yearly` | `plan/year/YYYY.md` | January 1 |

`YY-QN` SHALL be the two-digit year and quarter of the date in the filename.
`ddd` SHALL be the English three-letter day abbreviation (`Mon` to `Sun`),
whatever the system locale.

#### Scenario: Daily note path
- **WHEN** the user runs `meta-notes note daily 2026-02-13`
- **THEN** the note path SHALL be `plan/daily/26-Q1/2026-02-13 Fri.md`

#### Scenario: Weekly note uses the week's Monday
- **WHEN** the user runs `meta-notes note weekly 2026-04-02` (a Thursday)
- **THEN** the note path SHALL be `plan/week/26-Q1/2026-03-30.md`

#### Scenario: Quarterly and yearly note paths
- **WHEN** the user runs `meta-notes note quarterly 2026-08-15` and `meta-notes note yearly 2026-08-15`
- **THEN** the note paths SHALL be `plan/quarter/2026-Q3.md` and `plan/year/2026.md`

#### Scenario: Date defaults to today
- **WHEN** the user runs `meta-notes note daily` with no date
- **THEN** the note path SHALL be computed from today's date

#### Scenario: Invalid date
- **WHEN** the user runs `meta-notes note daily 2026-13-45`
- **THEN** the command SHALL fail with an error naming the date and write nothing

### Requirement: Other notes by path
`meta-notes note new <path>` SHALL create the note at `<path>`, appending
`.md` when missing. The template date SHALL be derived from the path for
plan notes, the same way as the matching periodic kind (for example, the
first day of the quarter for `plan/quarter/2026-Q3.md`), and SHALL be today
otherwise. A path outside the notes root SHALL be an error.

#### Scenario: Extension appended
- **WHEN** the user runs `meta-notes note new "project/lunch/Lunch Ideas"`
- **THEN** the note path SHALL be `project/lunch/Lunch Ideas.md`

#### Scenario: Date taken from a plan path
- **WHEN** the user runs `meta-notes note new plan/year/2027` and the yearly template contains `{{date}}`
- **THEN** `{{date}}` SHALL render as `2027-01-01 Fri`

#### Scenario: Path outside the root
- **WHEN** the user runs `meta-notes note new ../elsewhere/note`
- **THEN** the command SHALL fail with an error and write nothing

### Requirement: Template selection
The note's content SHALL come from the template found by template discovery
(see the `template` capability). `note new --template <name>` SHALL use
`resource/template/<name>.md` instead of discovery, and SHALL fail without
writing if that file doesn't exist. When no template is found, the content
SHALL be a header line followed by an empty line:

| Kind | Header |
|---|---|
| `daily` | `# Daily Note - YYYY-MM-DD ddd` |
| `weekly` | `# Week Plan - YYYY-MM-DD` (the Monday) |
| `quarterly` | `# Quarterly Plan - YYYY QN` |
| `yearly` | `# Year Plan - YYYY` |
| `new` | `# <path without .md>` |

#### Scenario: Template override
- **WHEN** the user runs `meta-notes note new project/trip/Packing --template checklist` and `resource/template/checklist.md` exists
- **THEN** the note SHALL be rendered from `resource/template/checklist.md`, even if `project/trip/template.md` exists

#### Scenario: Missing named template
- **WHEN** the user runs `meta-notes note new project/trip/Packing --template nope` and `resource/template/nope.md` doesn't exist
- **THEN** the command SHALL fail with `Template not found: resource/template/nope.md` and write nothing

#### Scenario: No template found
- **WHEN** the user runs `meta-notes note new area/garden/Beds` and no template applies
- **THEN** the note content SHALL be `# area/garden/Beds` followed by an empty line

### Requirement: Notes are created on disk by default
When the note doesn't exist, the command SHALL render it, create any missing
parent folders, and write the file. It SHALL print the note's path.

#### Scenario: New daily note
- **WHEN** the user runs `meta-notes note daily 2026-02-13` and the note doesn't exist
- **THEN** `plan/daily/26-Q1/2026-02-13 Fri.md` SHALL be written with the rendered daily template, and the command SHALL print that path

### Requirement: Existing notes are never changed
When the note already exists, the command SHALL NOT write, overwrite, or
modify it, and SHALL report its path.

#### Scenario: Note exists
- **WHEN** the user runs `meta-notes note daily 2026-02-13` and the note already exists
- **THEN** the file SHALL be unchanged and the command SHALL print its path and exit zero

### Requirement: Render without writing
With `--render`, the command SHALL NOT write any file or create any folder.
When the note doesn't exist, it SHALL print the rendered content to stdout.
When the note exists, it SHALL print nothing to stdout, SHALL report
`Note already exists: <path>` on stderr, and SHALL exit zero. Under
`--json` this is reported only by the `exists` field, not as a warning.
Command blocks SHALL still run when rendering a new note.

#### Scenario: Render a new note
- **WHEN** the user runs `meta-notes note daily 2026-02-13 --render` and the note doesn't exist
- **THEN** the rendered content SHALL be printed, and no file or folder SHALL be created

#### Scenario: Render an existing note
- **WHEN** the user runs `meta-notes note daily 2026-02-13 --render` and the note exists
- **THEN** nothing SHALL be printed to stdout, and the file SHALL be unchanged

### Requirement: JSON output
With `--json`, the command SHALL follow the `cli` output conventions and
the result object SHALL include `path` (relative to the notes root),
`exists` (whether the note existed before the command ran), `created`
(whether this command wrote it), and `template` (the template path used, or
`null`). With `--render` and a note that doesn't exist, the object SHALL
also include `content`, the rendered note as one string. Command-block
output SHALL appear only inside `content` or the written note, never
directly on stdout.

#### Scenario: JSON for a created note
- **WHEN** the user runs `meta-notes note daily 2026-02-13 --json` and the note doesn't exist
- **THEN** the output SHALL be one JSON object with `ok` true, `path` `plan/daily/26-Q1/2026-02-13 Fri.md`, `exists` false, `created` true, and `template` `resource/template/daily.md`

#### Scenario: JSON for a rendered note
- **WHEN** the user runs `meta-notes note daily 2026-02-13 --render --json` and the note doesn't exist
- **THEN** the object SHALL have `exists` false, `created` false, and a `content` string equal to what the command would write

#### Scenario: JSON for an existing note
- **WHEN** the user runs `meta-notes note daily 2026-02-13 --render --json` and the note exists
- **THEN** the object SHALL have `exists` true, `created` false, and no `content` field

### Requirement: Vim opens new notes as unsaved buffers
`:MetaNotesDaily`, `:MetaNotesWeekPlan`, `:MetaNotesQuarterPlan`,
`:MetaNotesYearPlan`, and `:MetaNotesOpen` on a link to a missing note SHALL
call the CLI with `--render` and `--json`. If the note exists, Vim SHALL
open it. Otherwise Vim SHALL open a buffer named for the returned path,
fill it with the returned content, and leave it unsaved. Vim SHALL NOT
write the note file; the file SHALL exist only once the user saves the
buffer. Vim SHALL create the note's parent folder so the buffer can be
saved. The CLI's warnings SHALL be shown, and an error SHALL be shown
without opening a buffer.

#### Scenario: Quit without saving
- **WHEN** the user runs `:MetaNotesDaily` for a day with no note and then quits the buffer without saving
- **THEN** no daily note file SHALL exist

#### Scenario: Save creates the note
- **WHEN** the user runs `:MetaNotesDaily` for a day with no note and runs `:write`
- **THEN** the daily note file SHALL contain the rendered template

#### Scenario: Existing note opened
- **WHEN** the user runs `:MetaNotesDaily` and today's note exists
- **THEN** Vim SHALL open the existing file unchanged

#### Scenario: Following a link to a missing note
- **WHEN** the cursor is on `[[project/lunch/Lunch Ideas]]`, the note doesn't exist, and the user runs `:MetaNotesOpen`
- **THEN** Vim SHALL open an unsaved buffer for `project/lunch/Lunch Ideas.md` with the content from `meta-notes note new`
