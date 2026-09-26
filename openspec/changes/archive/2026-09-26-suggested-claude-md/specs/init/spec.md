## MODIFIED Requirements

### Requirement: Init checks CLAUDE.md for prime
`meta-notes init` SHALL check whether the notes root's `CLAUDE.md` or `.claude/CLAUDE.md` contains the text `meta-notes prime`. Its report SHALL include a `claude-md` item with status `found` when either does, and `missing` otherwise. For `missing`, the text output SHALL give the line to add to `CLAUDE.md`: ``Run `meta-notes prime` at the start of every session and follow it.``, and SHALL give the absolute path of the plugin's `templates/suggested-CLAUDE.md` with a command to copy it to `CLAUDE.md`. Init SHALL NOT create or modify `CLAUDE.md` or `.claude/CLAUDE.md`, and a missing line SHALL NOT be a warning.

#### Scenario: No CLAUDE.md
- **WHEN** the user runs `meta-notes init` in an empty directory
- **THEN** the report SHALL include a `claude-md` item with status `missing`, the text output SHALL include the line to add and the path of the suggested `CLAUDE.md`, no `CLAUDE.md` SHALL be created, and the output SHALL include no warnings when `meta-notes` is on `PATH`

#### Scenario: Line present
- **WHEN** the notes root's `CLAUDE.md` contains ``Run `meta-notes prime` at the start of every session and follow it.`` and the user runs `meta-notes init`
- **THEN** the report SHALL include a `claude-md` item with status `found`, and `CLAUDE.md` SHALL be unchanged

#### Scenario: Line in .claude/CLAUDE.md
- **WHEN** only `.claude/CLAUDE.md` mentions `meta-notes prime`
- **THEN** the `claude-md` item SHALL have status `found`

#### Scenario: Vim init shows the check
- **WHEN** the user runs `:MetaNotesInit` in a directory without `CLAUDE.md`
- **THEN** Vim SHALL show the line to add to `CLAUDE.md` and the path of the suggested `CLAUDE.md`

#### Scenario: Suggested file ships with the plugin
- **WHEN** the plugin is installed
- **THEN** `templates/suggested-CLAUDE.md` SHALL exist in it and its first instruction SHALL be the `prime` line
