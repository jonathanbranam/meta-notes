## ADDED Requirements

### Requirement: Version reporting
The CLI SHALL accept `--version`, which reports the meta-notes version as `MAJOR.MINOR.PATCH` and exits zero without running a subcommand. `--version` SHALL NOT require a subcommand and SHALL NOT resolve a notes root, so it SHALL succeed from any directory. It SHALL take precedence over a subcommand given on the same command line.

Without `--json`, it SHALL print one line to stdout: `meta-notes <version>`. When the plugin directory is the top level of a git working tree, the line SHALL end with ` (<commit>)`, where `<commit>` is the short hash of the checked-out commit, followed by `-dirty` if tracked files have uncommitted changes. When the plugin directory is not the top level of a git working tree, or `git` is unavailable or fails, the line SHALL contain only the name and version, and no error or warning SHALL be reported.

With `--json`, it SHALL write one JSON object with `ok` set to true, `version`, `commit` (the short hash, or null), `dirty` (a boolean, false when `commit` is null), and `warnings`.

#### Scenario: Version from a git checkout
- **WHEN** `meta-notes --version` is run and the plugin directory is the top level of a clean git working tree
- **THEN** it SHALL exit zero and print `meta-notes <version> (<short hash>)`

#### Scenario: Version with uncommitted changes
- **WHEN** `meta-notes --version` is run and the plugin's git working tree has uncommitted changes to tracked files
- **THEN** the printed line SHALL end with `(<short hash>-dirty)`

#### Scenario: Version outside a git checkout
- **WHEN** `meta-notes --version` is run and the plugin directory is not the top level of a git working tree, including when it sits inside some other repository
- **THEN** it SHALL print `meta-notes <version>` with no commit, and nothing to stderr

#### Scenario: Version outside a notes root
- **WHEN** `meta-notes --version` is run from a directory with no `.meta-notes` at or above it, and neither `--root` nor `META_NOTES_ROOT` is set
- **THEN** it SHALL exit zero and report the version

#### Scenario: Version as JSON
- **WHEN** `meta-notes --version --json` is run
- **THEN** it SHALL write one JSON object to stdout with `ok` true, `version`, `commit`, `dirty`, and `warnings`, and nothing to stderr

#### Scenario: Version with a subcommand
- **WHEN** `meta-notes archive project/foo --version` is run
- **THEN** it SHALL report the version and SHALL NOT archive anything

### Requirement: Version in Vim
The plugin SHALL provide `:MetaNotesVersion`, which gets the version from the CLI's `--version --json` and echoes the same line that `meta-notes --version` prints. If the CLI fails, it SHALL show the error as an error message. It SHALL work whether or not Vim's current directory is in a notes root.

#### Scenario: Show version in Vim
- **WHEN** the user runs `:MetaNotesVersion`
- **THEN** Vim SHALL echo `meta-notes <version>`, followed by ` (<commit>)` when the CLI reports a commit

#### Scenario: CLI unavailable
- **WHEN** the user runs `:MetaNotesVersion` and the CLI can't be run
- **THEN** Vim SHALL show the error with the error highlight and SHALL NOT raise a Vim exception
