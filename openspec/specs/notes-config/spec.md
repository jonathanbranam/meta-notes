# notes-config Specification

## Purpose
Specifies the per-notes-root configuration that meta-notes reads from the `.meta-notes` sentinel as TOML, so commands can take settings such as the user's email and timezone without environment variables or extra files.

## Requirements

### Requirement: The sentinel is TOML config
The `.meta-notes` file at the notes root SHALL be read as TOML. A file containing only comments or blank lines, including the sentinel `init` writes, SHALL be valid and empty config. Settings SHALL be grouped in tables named for the command that uses them. Unknown tables and keys SHALL be ignored.

#### Scenario: Existing sentinel
- **WHEN** `.meta-notes` contains only `# meta-notes notes root. Created by `meta-notes init`; keep and commit it.`
- **THEN** a command that reads config SHALL run with every setting at its default

#### Scenario: Unknown key
- **WHEN** `.meta-notes` has `[calendar]` with `colour = "blue"` and `email = "me@example.com"`
- **THEN** `email` SHALL be used and `colour` SHALL be ignored without a warning or error

### Requirement: Config is read only where needed
Only commands that use settings SHALL read `.meta-notes` as config. When `.meta-notes` is not valid TOML, those commands SHALL fail with an error naming `.meta-notes` and the parse error's line; commands that don't use settings SHALL be unaffected, and finding the notes root SHALL still depend only on the file's existence.

#### Scenario: Invalid TOML
- **WHEN** `.meta-notes` contains `[calendar` and the user runs `meta-notes calendar`
- **THEN** the command SHALL exit non-zero with an error naming `.meta-notes` and the line of the error

#### Scenario: Other commands unaffected
- **WHEN** `.meta-notes` contains `[calendar` and the user runs `meta-notes tasks`
- **THEN** the command SHALL run as it would with a valid `.meta-notes`

### Requirement: Init does not rewrite config
`meta-notes init` SHALL NOT modify an existing `.meta-notes`, with or without `--force`, so settings the user adds are kept.

#### Scenario: Re-running init keeps settings
- **WHEN** `.meta-notes` has a `[calendar]` table and the user runs `meta-notes init --force`
- **THEN** `.meta-notes` SHALL be unchanged
