## Purpose

Specifies the behavior of the meta-notes template system: how templates are discovered when a note is created, what variables are available for substitution, how date features (arithmetic, format specifiers) work, and what inline command syntax is supported.

## Requirements

### Requirement: Template provides path-derived variables
The template system SHALL expose four variables derived from the file path of the note being created. All four are plain strings — date arithmetic and format specifiers do not apply to them.

| Variable | Value | Example for `project/lunch/Lunch Ideas.md` |
|---|---|---|
| `{{note_path}}` | Relative path without extension | `project/lunch/Lunch Ideas` |
| `{{note_name}}` | Filename stem (no extension) | `Lunch Ideas` |
| `{{filepath}}` | Relative path with extension | `project/lunch/Lunch Ideas.md` |
| `{{filename}}` | Filename with extension | `Lunch Ideas.md` |

#### Scenario: note_path resolves to relative path without extension
- **WHEN** a template contains `{{note_path}}` and the note being created is `project/lunch/Lunch Ideas.md`
- **THEN** `{{note_path}}` SHALL be replaced with `project/lunch/Lunch Ideas`

#### Scenario: note_name resolves to filename stem
- **WHEN** a template contains `{{note_name}}` and the note being created is `project/lunch/Lunch Ideas.md`
- **THEN** `{{note_name}}` SHALL be replaced with `Lunch Ideas`

#### Scenario: filepath resolves to full relative path with extension
- **WHEN** a template contains `{{filepath}}` and the note being created is `project/lunch/Lunch Ideas.md`
- **THEN** `{{filepath}}` SHALL be replaced with `project/lunch/Lunch Ideas.md`

#### Scenario: filename resolves to filename with extension
- **WHEN** a template contains `{{filename}}` and the note being created is `project/lunch/Lunch Ideas.md`
- **THEN** `{{filename}}` SHALL be replaced with `Lunch Ideas.md`

#### Scenario: note_name for a date-named file returns the stem unchanged
- **WHEN** a template contains `{{note_name}}` and the note being created is `plan/daily/26-Q2/2026-06-19.md`
- **THEN** `{{note_name}}` SHALL be replaced with `2026-06-19` (not `2026-06-19 Fri` or any date-formatted string)

### Requirement: Date features apply only to explicitly named date variables
The template system SHALL support date arithmetic (`{{variable+N}}`, `{{variable-N}}`) and strftime format specifiers (`{{variable:%format}}`) only for the variables `date`, `today`, `week_start`, and `week_end`. All other variables SHALL be substituted as plain strings regardless of their value's format.

#### Scenario: Arithmetic on a date variable is applied
- **WHEN** a template contains `{{date+7}}` and `date` is `2026-06-19`
- **THEN** it SHALL be replaced with `2026-06-26 Fri`

#### Scenario: Format specifier on a date variable is applied
- **WHEN** a template contains `{{today:%A}}` and today is a Friday
- **THEN** it SHALL be replaced with `Friday`

#### Scenario: A string variable with a date-shaped value is not processed as a date
- **WHEN** `note_name` is `2026-06-19` (a date-named file) and a template contains `{{note_name}}`
- **THEN** it SHALL be replaced with `2026-06-19` and SHALL NOT be formatted as `2026-06-19 Fri`

#### Scenario: Unknown variable produces an error comment
- **WHEN** a template contains `{{unknown_var}}`
- **THEN** it SHALL be replaced with `<!-- ERROR: Unknown variable "unknown_var" -->`

### Requirement: Template provides the week's quarter
The template system SHALL expose `{{week_quarter}}`, the quarter (`Q1` to
`Q4`) that contains `week_start`, the Monday of the note's week. It SHALL be
a plain string: date arithmetic and format specifiers SHALL NOT apply to it.
`{{quarter}}` SHALL keep its meaning, the quarter of the note's date.

#### Scenario: Week starting in the previous quarter
- **WHEN** a note's date is `2026-04-02` (a Thursday whose Monday is `2026-03-30`) and a template contains `{{quarter}} {{week_quarter}}`
- **THEN** it SHALL be replaced with `Q2 Q1`

#### Scenario: Week starting in the previous year
- **WHEN** a note's date is `2026-01-01` (a Thursday whose Monday is `2025-12-29`) and a template contains `{{week_quarter}}`
- **THEN** it SHALL be replaced with `Q4`

#### Scenario: Week within one quarter
- **WHEN** a note's date is `2026-02-13` and a template contains `{{week_quarter}}`
- **THEN** it SHALL be replaced with `Q1`

### Requirement: Shipped daily template links to its week plan
The daily template shipped with the plugin SHALL link to the week plan with
a wiki-link whose path, with `.md` appended, is the path of the weekly note
for the daily note's date (see the `note-create` capability's periodic note
paths), for every date.

#### Scenario: Week plan link across a quarter boundary
- **WHEN** the shipped daily template is rendered for `2026-04-02`
- **THEN** it SHALL contain `[[plan/week/26-Q1/2026-03-30]]`, and `meta-notes note weekly 2026-04-02` SHALL report the path `plan/week/26-Q1/2026-03-30.md`

#### Scenario: Week plan link across a year boundary
- **WHEN** the shipped daily template is rendered for `2026-01-01`
- **THEN** it SHALL contain `[[plan/week/25-Q4/2025-12-29]]`

### Requirement: Template system is documented
The plugin SHALL document the template system in `doc/meta-notes.txt` section 6, accessible via `:help meta-notes-templates`, covering folder template resolution priority, all supported variables with their options, the `{{% type command %}}` syntax, and that templates are rendered by `meta-notes note`, with `{{% vim %}}` blocks run only when a note is opened in Vim.

#### Scenario: Documentation covers all supported variables
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document `date`, `today`, `week_start`, `week_end`, `quarter`, `week_quarter`, `project_name`, `note_path`, `note_name`, `filepath`, and `filename` with descriptions and examples

#### Scenario: Documentation covers template resolution order
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL describe the resolution order: `--template` when given, folder-specific `template.md`, then the standard template for plan folders

#### Scenario: Documentation covers command syntax
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document the `{{% vim %}}`, `{{% python %}}`, and `{{% shell %}}` command forms with examples, and SHALL state that `{{% vim %}}` blocks are left as text in notes created outside Vim

### Requirement: Templates are rendered by the CLI
Template discovery and rendering SHALL be performed by the `meta-notes`
CLI. The Vim plugin SHALL obtain rendered note content from the CLI and
SHALL NOT substitute variables or run `python` or `shell` command blocks
itself. Rendering the existing templates SHALL produce the same content as
the Vim implementation did.

#### Scenario: Same output as Vim
- **WHEN** the shipped daily template is rendered for `2026-02-13` with command blocks whose output is fixed
- **THEN** the content SHALL match what the Vim implementation produced for the same date and command output

### Requirement: Template discovery
For a note at `<dir>/<name>.md`, the template SHALL be, in order: `<dir>/template.md` if it exists; otherwise, for a note under `plan/daily/`, `plan/week/`, `plan/quarter/`, or `plan/year/`, `resource/template/daily.md`, `weekly.md`, `quarterly.md`, or `yearly.md` respectively, if it exists; otherwise no template.

#### Scenario: Folder template wins
- **WHEN** a note is created at `project/trip/Packing.md` and `project/trip/template.md` exists
- **THEN** the note SHALL be rendered from `project/trip/template.md`

#### Scenario: Standard plan template
- **WHEN** a note is created under `plan/week/26-Q1/` and that folder has no `template.md`
- **THEN** the note SHALL be rendered from `resource/template/weekly.md`

### Requirement: Frontmatter is stripped
A YAML frontmatter block at the top of a template, delimited by `---`
lines, SHALL NOT appear in the rendered note.

#### Scenario: Template with frontmatter
- **WHEN** a template starts with `---`, `filename_pattern: "..."`, `---`, `# Title`
- **THEN** the rendered note SHALL start with `# Title`

### Requirement: Command blocks
A template line containing `{{% <type> <command> %}}` SHALL be replaced by
the output of the command, split into lines. Variables in the command SHALL
be substituted before it runs. Commands SHALL run with the notes root as
the working directory.

- `python`: runs the command with Python 3. A command starting with
  `scripts/` SHALL resolve to the plugin's `scripts/` directory.
- `shell`: runs the command in the shell.
- `vim`: SHALL NOT be run by the CLI. The line SHALL be kept in the output
  with variables in the command substituted. When Vim fills a buffer with
  rendered content, it SHALL run each such block as a Vim command and
  replace the line with the command's output. A note written by the CLI
  keeps the line as text, and the CLI SHALL report a warning.
- Any other type SHALL be replaced by `<!-- Unknown command type: <type> -->`.

A `python` or `shell` command that exits non-zero SHALL be replaced by
`<!-- Command failed: <original line>` followed by a line
`Error: <command output> -->`. The note SHALL still be created, and the CLI
SHALL report a warning naming the failed command.

#### Scenario: Script from the plugin
- **WHEN** a template contains `{{% python scripts/find_tasks.py --due --date {{date:%Y-%m-%d}} --condensed %}}` and is rendered for `2026-02-13`
- **THEN** the plugin's `scripts/find_tasks.py` SHALL run from the notes root with `--due --date 2026-02-13 --condensed`, and its output SHALL replace the line

#### Scenario: Shell command
- **WHEN** a template contains `{{% shell echo "- Task from shell" %}}`
- **THEN** the line SHALL be replaced by `- Task from shell`

#### Scenario: Failed command
- **WHEN** a template contains `{{% shell exit 1 %}}`
- **THEN** the note SHALL be created with a `<!-- Command failed: {{% shell exit 1 %}}` comment in its place, and the CLI SHALL report a warning

#### Scenario: Vim block rendered in Vim
- **WHEN** a template contains `{{% vim echo "{{date}}" %}}` and the user opens a new note from it in Vim
- **THEN** the CLI output SHALL contain the block with the date substituted, and the unsaved buffer SHALL contain the command's output in its place

#### Scenario: Vim block written by the CLI
- **WHEN** a note whose template contains a `{{% vim ... %}}` block is created by `meta-notes note` without `--render`
- **THEN** the written note SHALL contain the block as text, and the CLI SHALL report a warning

#### Scenario: Unknown command type
- **WHEN** a template contains `{{% unknown some command %}}`
- **THEN** the line SHALL be replaced by `<!-- Unknown command type: unknown -->`

#### Scenario: Script called with removed options
- **WHEN** a template copied before this release contains `{{% python scripts/find_tasks.py --due-on {{date:%Y-%m-%d}} --condensed %}}`
- **THEN** the note SHALL be created with a `<!-- Command failed: ...` comment containing the usage error in its place, and the CLI SHALL report a warning

### Requirement: Shipped daily template task sections
The shipped daily template's "Tasks Due Today" section SHALL list incomplete tasks due on the note's date, and its "Overdue Tasks" section SHALL list incomplete tasks due before the note's date, both in condensed format, using `--due` and `--overdue` with `--date` set to the note's date.

#### Scenario: Daily note task sections
- **WHEN** a daily note is created for 2026-09-25
- **THEN** its template SHALL run `find_tasks.py --due --date 2026-09-25 --condensed` for "Tasks Due Today" and `find_tasks.py --overdue --date 2026-09-25 --condensed` for "Overdue Tasks"
