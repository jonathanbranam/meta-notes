## ADDED Requirements

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

### Requirement: Template system is documented
The plugin SHALL include a `doc/templates.md` reference file covering folder template resolution priority, all supported variables with their options, and the `{{% type command %}}` syntax.

#### Scenario: Documentation covers all supported variables
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document `date`, `today`, `week_start`, `week_end`, `quarter`, `project_name`, `note_path`, `note_name`, `filepath`, and `filename` with descriptions and examples

#### Scenario: Documentation covers template resolution order
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL describe the three-step resolution order: folder-specific `template.md`, named standard template, auto-detected standard template

#### Scenario: Documentation covers command syntax
- **WHEN** a user runs `:help meta-notes-templates`
- **THEN** the section SHALL document the `{{% vim %}}`, `{{% python %}}`, and `{{% shell %}}` command forms with examples
