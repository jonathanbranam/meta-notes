# notes-config Specification

## Purpose
Specifies the per-notes-root configuration that meta-notes reads from the `.meta-notes` sentinel as TOML, so commands can take settings such as the user's email and timezone without environment variables or extra files.

## Requirements

### Requirement: The sentinel is TOML config  {#r-d982}
The `.meta-notes` file at the notes root SHALL be read as TOML. A file containing only comments or blank lines, including the sentinel `init` writes, SHALL be valid and empty config. Settings SHALL be grouped in tables named for the command that uses them. Unknown tables and keys SHALL be ignored.

#### Scenario: Existing sentinel  {#s-9cab}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` contains only `# meta-notes notes root. Created by `meta-notes init`; keep and commit it.`
- **THEN** a command that reads config SHALL run with every setting at its default

#### Scenario: Unknown key  {#s-4289}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has `[calendar]` with `colour = "blue"` and `email = "me@example.com"`
- **THEN** `email` SHALL be used and `colour` SHALL be ignored without a warning or error

### Requirement: Config is read only where needed  {#r-d209}
Only commands that use settings SHALL read `.meta-notes` as config. When `.meta-notes` is not valid TOML, those commands SHALL fail with an error naming `.meta-notes` and the parse error's line; commands that don't use settings SHALL be unaffected, and finding the notes root SHALL still depend only on the file's existence.

#### Scenario: Invalid TOML  {#s-1775}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` contains `[calendar` and the user runs `meta-notes calendar`
- **THEN** the command SHALL exit non-zero with an error naming `.meta-notes` and the line of the error

#### Scenario: Other commands unaffected  {#s-98dd}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` contains `[calendar` and the user runs `meta-notes tasks`
- **THEN** the command SHALL run as it would with a valid `.meta-notes`

### Requirement: Init does not rewrite config  {#r-7c4f}
`meta-notes init` SHALL NOT modify an existing `.meta-notes`, with or without `--force`, so settings the user adds are kept.

#### Scenario: Re-running init keeps settings  {#s-0766}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has a `[calendar]` table and the user runs `meta-notes init --force`
- **THEN** `.meta-notes` SHALL be unchanged

### Requirement: Root mode  {#r-4b1e}
`.meta-notes` MAY set the top-level key `mode` to `"work"` or `"personal"`. When it is absent, the mode SHALL be `work`, so existing roots behave as before. Any other value SHALL be an error naming the two choices. Commands that depend on the mode SHALL read it through one accessor, `config.mode(root)`. `meta-notes prime` and `meta-notes conventions` SHALL report it, and `--json` output that depends on the mode SHALL carry `mode`.

#### Scenario: Mode absent  {#s-a3f1}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has no `mode` key and the user runs `meta-notes prime --json`
- **THEN** `mode` SHALL be `work`

#### Scenario: Personal mode  {#s-c7d2}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has `mode = "personal"` and the user runs `meta-notes prime`
- **THEN** the guide SHALL state that the root is in personal mode

#### Scenario: Invalid mode  {#s-e905}
*Verification*: **non-executable**
- **WHEN** `.meta-notes` has `mode = "home"` and the user runs `meta-notes prime`
- **THEN** the command SHALL exit non-zero with an error naming `work` and `personal`
