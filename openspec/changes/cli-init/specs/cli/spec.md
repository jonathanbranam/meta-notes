## MODIFIED Requirements

### Requirement: Notes root resolution
The CLI SHALL resolve the notes root from `--root`, then the `META_NOTES_ROOT` environment variable, then an upward search from the current directory for the nearest directory containing a `.meta-notes` sentinel file. An explicit `--root` or `META_NOTES_ROOT` SHALL be used as given, whether or not it contains `.meta-notes`. Paths in arguments and output SHALL be relative to the notes root. `init` is exempt: it initializes the directory it is given and does not resolve a root.

The upward search SHALL:
- check each directory only for a `.meta-notes` file, and SHALL NOT list any directory's contents
- identify a notes root by `.meta-notes` alone, not by folder names such as `plan/`, `project/`, or `area/`
- stop after checking `$HOME`
- stop, without reporting an error for that directory, at the first directory the user cannot read, write, and search, without checking it

If the search stops without finding `.meta-notes`, the command SHALL fail with an error that says no notes root was found and to run `meta-notes init` in the notes root or to pass `--root`.

#### Scenario: Root found by walking up
- **WHEN** the CLI is run from `project/foo/` inside a notes root that contains `.meta-notes`, and neither `--root` nor `META_NOTES_ROOT` is set
- **THEN** the notes root SHALL be the directory containing `.meta-notes`

#### Scenario: Folder names alone do not make a root
- **WHEN** the CLI is run without `--root` or `META_NOTES_ROOT` from a directory whose ancestor contains `plan/`, `project/`, and `area/` but no `.meta-notes`, and no other ancestor up to `$HOME` contains `.meta-notes`
- **THEN** the CLI SHALL exit non-zero with the no-notes-root error

#### Scenario: Explicit root without plan folder
- **WHEN** the CLI is run with `--root <dir>` and `<dir>` has no `.meta-notes` and no `plan/` folder
- **THEN** the CLI SHALL use `<dir>` as the notes root

#### Scenario: Search stops at $HOME
- **WHEN** the CLI is run from a directory under `$HOME`, and only a directory above `$HOME` contains `.meta-notes`
- **THEN** the CLI SHALL exit non-zero with the no-notes-root error

#### Scenario: Search stops at a directory without permission
- **WHEN** the CLI is run from `a/b/` where `a/` contains `.meta-notes` but the user cannot write to `a/`
- **THEN** the CLI SHALL exit non-zero with the no-notes-root error, and SHALL NOT report a permission error

#### Scenario: No root found
- **WHEN** no root can be resolved
- **THEN** the CLI SHALL exit non-zero with an error that says to run `meta-notes init` or pass `--root`
