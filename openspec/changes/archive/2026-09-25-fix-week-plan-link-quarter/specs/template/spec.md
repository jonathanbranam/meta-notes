## ADDED Requirements

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

## MODIFIED Requirements

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
