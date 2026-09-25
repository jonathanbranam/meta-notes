## ADDED Requirements

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
- **WHEN** a template contains `{{% python scripts/find_tasks.py --due-on {{date:%Y-%m-%d}} --condensed %}}` and is rendered for `2026-02-13`
- **THEN** the plugin's `scripts/find_tasks.py` SHALL run from the notes root with `--due-on 2026-02-13 --condensed`, and its output SHALL replace the line

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

## MODIFIED Requirements

### Requirement: Template system is documented
The plugin SHALL document the template system in `doc/meta-notes.txt` section 6, accessible via `:help meta-notes-templates`, covering folder template resolution priority, all supported variables with their options, the `{{% type command %}}` syntax, and that templates are rendered by `meta-notes note`, with `{{% vim %}}` blocks run only when a note is opened in Vim.

#### Scenario: Documentation covers all supported variables
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document `date`, `today`, `week_start`, `week_end`, `quarter`, `project_name`, `note_path`, `note_name`, `filepath`, and `filename` with descriptions and examples

#### Scenario: Documentation covers template resolution order
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL describe the resolution order: `--template` when given, folder-specific `template.md`, then the standard template for plan folders

#### Scenario: Documentation covers command syntax
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document the `{{% vim %}}`, `{{% python %}}`, and `{{% shell %}}` command forms with examples, and SHALL state that `{{% vim %}}` blocks are left as text in notes created outside Vim
