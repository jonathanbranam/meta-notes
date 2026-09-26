## MODIFIED Requirements

### Requirement: File operations are implemented by the CLI
The system SHALL provide a `meta-notes` command, written in Python, that implements move, rename, and archive. Commands SHALL use only the Python standard library, except where a command's own spec says it needs other libraries; those libraries SHALL be installed only in the notes root's virtualenv and imported only by the commands that need them. The Vim plugin SHALL perform these operations by invoking the CLI and SHALL NOT move files or rewrite headers or links itself.

#### Scenario: Vim archive uses the CLI
- **WHEN** the user runs `:MetaNotesArchive project/foo`
- **THEN** the plugin SHALL invoke `meta-notes archive` with `--root` set to Vim's current directory and `--json`

#### Scenario: Agent can archive without Vim
- **WHEN** `meta-notes archive project/foo` is run from a shell in the notes root
- **THEN** the resulting files and links SHALL be identical to running `:MetaNotesArchive project/foo` in Vim

#### Scenario: Standard-library commands work without the virtualenv
- **WHEN** the notes root has no `.venv` and the user runs `meta-notes tasks --json`
- **THEN** the command SHALL succeed using the `python3` on `PATH`

## ADDED Requirements

### Requirement: Python version
The CLI SHALL require Python 3.11 or newer. On an older Python, every command SHALL exit non-zero with an error that names the required and found versions; with `--json`, the error SHALL be a single JSON object with `ok` false.

#### Scenario: Python 3.10
- **WHEN** `meta-notes tasks --json` runs on Python 3.10
- **THEN** stdout SHALL be one JSON object with `ok` false and an error saying Python 3.11 or newer is required and 3.10 was found

### Requirement: The command runs the notes root's virtualenv
`bin/meta-notes` SHALL run the CLI with `<root>/.venv/bin/python3` when that file exists and is executable, and with the `python3` on `PATH` otherwise. `<root>` SHALL be found as in "Notes root resolution": the `--root` value (given as `--root DIR` or `--root=DIR`, before or after the subcommand), then `META_NOTES_ROOT`, then an upward search from the current directory for `.meta-notes` that stops after `$HOME`. `meta-notes init` SHALL always run with the `python3` on `PATH`. The interpreter choice SHALL NOT change which notes root the command uses.

#### Scenario: Virtualenv present
- **WHEN** the notes root has an executable `.venv/bin/python3` and the user runs `meta-notes calendar` from `project/foo/` inside it
- **THEN** the CLI SHALL run with `<root>/.venv/bin/python3`

#### Scenario: Root passed after the subcommand
- **WHEN** Vim runs `bin/meta-notes calendar --root /notes --json` from a directory outside `/notes`, and `/notes/.venv/bin/python3` is executable
- **THEN** the CLI SHALL run with `/notes/.venv/bin/python3`

#### Scenario: Broken virtualenv
- **WHEN** `.venv/bin/python3` is a link to an interpreter that no longer exists
- **THEN** the CLI SHALL run with the `python3` on `PATH`

#### Scenario: Init ignores the virtualenv
- **WHEN** the notes root has an executable `.venv/bin/python3` and the user runs `meta-notes init --force` in it
- **THEN** init SHALL run with the `python3` on `PATH`
