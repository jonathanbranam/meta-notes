## Purpose

Specifies `meta-notes init` and `:MetaNotesInit`, which set up a notes root: the PPARA folders, the planning templates, the `.meta-notes` sentinel that identifies the root, and the Claude Code skills the plugin ships. Covers where init runs, what re-runs and `--force` do, and the rule that notes roots never nest.

## ADDED Requirements

### Requirement: Init creates the notes root structure
`meta-notes init` SHALL create, in the target directory, any of the following that are missing:
- the folders `plan/`, `plan/daily/`, `plan/week/`, `plan/quarter/`, `plan/year/`, `project/`, `area/`, `resource/`, `resource/template/`, `archive/`, `archive/project/`, `archive/area/`, and `archive/resource/`
- the templates `resource/template/daily.md`, `weekly.md`, `quarterly.md`, and `yearly.md`
- the sentinel file `.meta-notes`

The template files SHALL have the same content that `:MetaNotesInit` wrote before this change.

#### Scenario: Init in an empty directory
- **WHEN** the user runs `meta-notes init` in an empty directory
- **THEN** every listed folder, every listed template, and `.meta-notes` SHALL exist in that directory

#### Scenario: Template content unchanged
- **WHEN** `meta-notes init` creates `resource/template/daily.md`
- **THEN** its content SHALL be identical to the `daily.md` that `:MetaNotesInit` created before this change, and likewise for `weekly.md`, `quarterly.md`, and `yearly.md`

### Requirement: Init targets the directory it is given
`meta-notes init` SHALL initialize the `--root` directory when given, otherwise the current directory. It SHALL NOT search for an existing notes root to decide where to initialize, and SHALL ignore `META_NOTES_ROOT`. If the `--root` directory does not exist, init SHALL create it, including missing parents.

#### Scenario: Init the current directory
- **WHEN** the user runs `meta-notes init` without `--root`
- **THEN** the current directory SHALL be initialized

#### Scenario: Init with --root
- **WHEN** the user runs `meta-notes init --root <dir>` and `<dir>` exists
- **THEN** `<dir>` SHALL be initialized

#### Scenario: Init a new directory
- **WHEN** the user runs `meta-notes init --root notes/personal` and `notes/personal` does not exist
- **THEN** `notes/personal` SHALL be created, including `notes/` if missing, and initialized

#### Scenario: META_NOTES_ROOT is ignored
- **WHEN** `META_NOTES_ROOT` is set to another notes root and the user runs `meta-notes init` in an empty directory
- **THEN** the current directory SHALL be initialized and the root named by `META_NOTES_ROOT` SHALL be unchanged

### Requirement: Notes roots never nest
Before changing anything, `meta-notes init` SHALL search upward from the target's parent for a `.meta-notes` sentinel, using the same bounded search that other commands use to find a notes root. If it finds one, init SHALL fail with an error naming that root and make no changes. `--force` SHALL NOT override this. A target that already contains `.meta-notes` SHALL NOT count as nested.

#### Scenario: Init inside an existing root
- **WHEN** the user runs `meta-notes init` in `project/foo/` of a notes root that contains `.meta-notes`
- **THEN** the command SHALL fail with an error naming the notes root, and `project/foo/` SHALL be unchanged

#### Scenario: Force does not allow nesting
- **WHEN** the user runs `meta-notes init --force` in `project/foo/` of a notes root that contains `.meta-notes`
- **THEN** the command SHALL fail and make no changes

#### Scenario: Re-running in a root is not nesting
- **WHEN** the user runs `meta-notes init` in a directory that already contains `.meta-notes`
- **THEN** the command SHALL succeed

### Requirement: Re-running init is non-destructive
Running `meta-notes init` in an existing notes root SHALL create only what is missing. Without `--force`, it SHALL NOT modify or remove any existing folder, template, sentinel, or note. With `--force`, it SHALL overwrite the four templates with their shipped content, and SHALL still not modify or remove notes or the sentinel.

#### Scenario: Existing root without a sentinel
- **WHEN** the user runs `meta-notes init` in a populated notes root created before this change, which has no `.meta-notes`
- **THEN** `.meta-notes` and any missing folders and templates SHALL be created, and every existing file SHALL be unchanged

#### Scenario: Modified template is kept
- **WHEN** `resource/template/daily.md` has been edited and the user runs `meta-notes init`
- **THEN** `resource/template/daily.md` SHALL keep the edited content

#### Scenario: Force restores templates
- **WHEN** `resource/template/daily.md` has been edited and the user runs `meta-notes init --force`
- **THEN** `resource/template/daily.md` SHALL have the shipped content, and no note outside `resource/template/` SHALL be changed

### Requirement: Init installs the shipped skills
For every skill the plugin ships in its `skills/` directory, `meta-notes init` SHALL make `<root>/.claude/skills/<name>` a symbolic link to the plugin's copy of that skill, creating `.claude/skills/` if needed. On a re-run:
- a link that already points to the plugin's copy SHALL be left alone
- a link that points elsewhere, or whose target is missing, SHALL be repointed to the plugin's copy
- a file or directory that is not a link SHALL be left alone and reported as a warning; the command SHALL still succeed
- with `--force`, a file or directory that is not a link SHALL be replaced by the link

Init SHALL NOT remove links for skills the plugin no longer ships.

#### Scenario: Skills installed on first run
- **WHEN** the plugin ships `skills/project-review/` and the user runs `meta-notes init`
- **THEN** `.claude/skills/project-review` SHALL be a link that resolves to the plugin's `skills/project-review/`

#### Scenario: Plugin update reaches the notes root
- **WHEN** the plugin's `skills/project-review/SKILL.md` changes after init
- **THEN** reading `.claude/skills/project-review/SKILL.md` in the notes root SHALL give the changed content without re-running init

#### Scenario: Stale link repointed
- **WHEN** `.claude/skills/project-review` is a link to a directory that no longer exists and the user runs `meta-notes init`
- **THEN** the link SHALL be repointed to the plugin's copy

#### Scenario: Real directory kept with a warning
- **WHEN** `.claude/skills/project-review` is a real directory and the user runs `meta-notes init`
- **THEN** the directory and its contents SHALL be unchanged, the command SHALL succeed, and its output SHALL include a warning naming `.claude/skills/project-review`

#### Scenario: Force replaces a real directory
- **WHEN** `.claude/skills/project-review` is a real directory and the user runs `meta-notes init --force`
- **THEN** it SHALL be replaced by a link to the plugin's copy

### Requirement: Init warns when the CLI is not on PATH
Skills call `meta-notes` by name, so it must be on `PATH`. When no `meta-notes` command is found on `PATH`, `meta-notes init` SHALL still succeed and SHALL report a warning that gives the command to link the plugin's `bin/meta-notes` into a directory on `PATH`.

#### Scenario: CLI not on PATH
- **WHEN** no `meta-notes` is on `PATH` and the user runs `meta-notes init` by its full path
- **THEN** the command SHALL succeed and its output SHALL include a warning containing the absolute path of the plugin's `bin/meta-notes`

#### Scenario: CLI on PATH
- **WHEN** `meta-notes` is on `PATH` and the user runs `meta-notes init` in an empty directory
- **THEN** its output SHALL include no warnings

### Requirement: Init reports what it did
`meta-notes init` SHALL report, for each folder, template, the sentinel, and each skill, whether it was created, already existed, was overwritten, or was skipped. With `--json`, this report SHALL be part of the single JSON object, and skill conflicts left alone SHALL appear in `warnings`.

#### Scenario: JSON report
- **WHEN** the user runs `meta-notes init --json` in an empty directory
- **THEN** stdout SHALL be one JSON object with `ok` true that lists each folder, template, the sentinel, and each skill as created

### Requirement: Vim init uses the CLI
`:MetaNotesInit` SHALL initialize Vim's current directory by invoking `meta-notes init` with `--root` set to that directory and `--json`, and `:MetaNotesInit!` SHALL add `--force`. The plugin SHALL NOT create the folders, templates, or skill links itself. It SHALL show a message for each folder and template, as before this change, and for the sentinel and each skill.

#### Scenario: Vim init
- **WHEN** the user runs `:MetaNotesInit` in Vim with the current directory set to an empty directory
- **THEN** the directory SHALL contain the same folders, templates, sentinel, and skill links as after `meta-notes init` run in that directory

#### Scenario: Vim init with bang
- **WHEN** `resource/template/daily.md` has been edited and the user runs `:MetaNotesInit!`
- **THEN** `resource/template/daily.md` SHALL have the shipped content
