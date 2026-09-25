## ADDED Requirements

### Requirement: File operations are implemented by the CLI
The system SHALL provide a `meta-notes` command, written in Python using only the standard library, that implements move, rename, and archive. The Vim plugin SHALL perform these operations by invoking the CLI and SHALL NOT move files or rewrite headers or links itself.

#### Scenario: Vim archive uses the CLI
- **WHEN** the user runs `:MetaNotesArchive project/foo`
- **THEN** the plugin SHALL invoke `meta-notes archive` with `--root` set to Vim's current directory and `--json`

#### Scenario: Agent can archive without Vim
- **WHEN** `meta-notes archive project/foo` is run from a shell in the notes root
- **THEN** the resulting files and links SHALL be identical to running `:MetaNotesArchive project/foo` in Vim

### Requirement: Notes root resolution
The CLI SHALL resolve the notes root from `--root`, then the `META_NOTES_ROOT` environment variable, then the nearest ancestor of the current directory containing `plan/`, `project/`, and `area/`. Paths in arguments and output SHALL be relative to the notes root.

#### Scenario: Root found by walking up
- **WHEN** the CLI is run from `project/foo/` inside a notes root and neither `--root` nor `META_NOTES_ROOT` is set
- **THEN** the notes root SHALL be the directory containing `plan/`, `project/`, and `area/`

#### Scenario: Explicit root without plan folder
- **WHEN** the CLI is run with `--root <dir>` and `<dir>` has no `plan/` folder
- **THEN** the CLI SHALL use `<dir>` as the notes root

#### Scenario: No root found
- **WHEN** no root can be resolved
- **THEN** the CLI SHALL exit non-zero with an error

### Requirement: Machine-readable output
Every command SHALL accept `--json`. With `--json`, the command SHALL write exactly one JSON object to stdout and nothing to stderr, whether it succeeds or fails. Without `--json`, errors and warnings SHALL go to stderr.

#### Scenario: Error with --json
- **WHEN** a command fails with `--json`
- **THEN** it SHALL exit non-zero and write one JSON object to stdout with `ok` set to false and an `error` message

#### Scenario: Error without --json
- **WHEN** a command fails without `--json`
- **THEN** it SHALL exit non-zero and write the error to stderr

### Requirement: Move handles notes, folders, and hierarchies
`meta-notes move <src> <dst>` SHALL move a note, a folder, or a folder hierarchy including non-markdown files, rewrite the first line of each moved note that is exactly `# <old path>`, and rewrite every `[[old path]]` and `[[old path/...]]` wiki-link to a moved path.

#### Scenario: Project converted to an area
- **WHEN** the user runs `meta-notes move project/foo area/foo`
- **THEN** all contents SHALL appear under `area/foo` and every link to `project/foo` or any path beneath it SHALL be rewritten to the corresponding `area/foo` path

#### Scenario: Header rewritten
- **WHEN** `project/foo.md` begins with `# project/foo` and is moved to `area/foo`
- **THEN** `area/foo.md` SHALL begin with `# area/foo`

#### Scenario: Target exists
- **WHEN** the destination file already exists
- **THEN** the command SHALL fail with `Target file already exists: <dst>` and make no changes

### Requirement: Rename keeps the directory for bare names
`meta-notes rename <src> <new-name>` SHALL keep the source's directory when `<new-name>` contains no `/`, SHALL append `.md` when missing, and SHALL otherwise behave as `move`.

#### Scenario: Bare name
- **WHEN** the user runs `meta-notes rename project/foo.md bar`
- **THEN** the note SHALL be moved to `project/bar.md` with its header and links updated

### Requirement: Archive accepts wildcards
`meta-notes archive` SHALL expand `*` and `?` in its path argument and archive each match independently, continuing past items that fail and reporting each failure.

#### Scenario: Batch archive
- **WHEN** the user runs `meta-notes archive 'project/batch/*.md'` and the folder contains three notes
- **THEN** all three notes SHALL be moved under `archive/project/batch/`

### Requirement: No git writes
The CLI and the Vim plugin SHALL NOT stage or commit changes.

#### Scenario: Move in a git repository
- **WHEN** `meta-notes rename project/foo.md bar` runs in a notes root that is a git repository
- **THEN** the note SHALL be renamed and links rewritten in the working tree, and the index and commit history SHALL be unchanged
