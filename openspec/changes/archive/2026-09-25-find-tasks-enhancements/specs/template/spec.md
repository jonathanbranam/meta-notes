## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Shipped daily template task sections
The shipped daily template's "Tasks Due Today" section SHALL list incomplete tasks due on the note's date, and its "Overdue Tasks" section SHALL list incomplete tasks due before the note's date, both in condensed format, using `--due` and `--overdue` with `--date` set to the note's date.

#### Scenario: Daily note task sections
- **WHEN** a daily note is created for 2026-09-25
- **THEN** its template SHALL run `find_tasks.py --due --date 2026-09-25 --condensed` for "Tasks Due Today" and `find_tasks.py --overdue --date 2026-09-25 --condensed` for "Overdue Tasks"
