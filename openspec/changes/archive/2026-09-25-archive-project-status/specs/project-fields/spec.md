## Purpose

Defines a project's home note and the `key: value` field list in it (`status`, `tag`, `archived`), so every command that reads or writes project fields finds and edits them the same way.

## ADDED Requirements

### Requirement: Projects and home notes
A project SHALL be a `.md` note directly in `project/` (or `archive/project/`) or a folder directly in one of them. A note project's home note SHALL be the note itself. A folder project's home note SHALL be its `Home.md`; a folder with no `Home.md` SHALL have no home note. Notes and folders nested deeper SHALL NOT be projects.

#### Scenario: Note project
- **WHEN** the notes root has `project/make-bread.md`
- **THEN** it SHALL be a project whose home note is `project/make-bread.md`

#### Scenario: Folder project
- **WHEN** the notes root has `project/kitchen/Home.md` and `project/kitchen/Tasks.md`
- **THEN** `project/kitchen/` SHALL be a project whose home note is `project/kitchen/Home.md`, and `project/kitchen/Tasks.md` SHALL NOT be a project

#### Scenario: Folder without a home note
- **WHEN** `project/trip/` has notes but no `Home.md`
- **THEN** `project/trip/` SHALL be a project with no home note

### Requirement: Field list
A home note's title SHALL be its first heading line. A field item SHALL be a list item of the form `- key: value`, where `key` is letters, digits, `-`, or `_`, and the item is not a task checkbox. The field list SHALL be the first list after the title, before any other heading, when it contains at least one field item. A home note with no title SHALL use the first list at the top of the note (before any heading) under the same rule. A home note with no such list SHALL have no field list. The project's fields SHALL be the field items of the field list. Keys SHALL be compared ignoring case. Frontmatter SHALL NOT be read.

#### Scenario: Fields read
- **WHEN** a home note is `# Make Bread`, a blank line, `- status: paused`, `- tag: make-bread`
- **THEN** its fields SHALL be `status` `paused` and `tag` `make-bread`

#### Scenario: Task list is not a field list
- **WHEN** a home note is `# Make Bread`, a blank line, `- [ ] Buy a banneton #next`
- **THEN** it SHALL have no field list

#### Scenario: List under a later heading ignored
- **WHEN** a home note is `# Make Bread`, a blank line, `## Notes`, `- status: paused`
- **THEN** it SHALL have no field list

#### Scenario: No title
- **WHEN** a home note starts with `- status: waiting` and has no heading
- **THEN** its `status` field SHALL be `waiting`

### Requirement: Setting fields
Setting a field SHALL replace the value of the first field item with that key and remove any later items with the same key, keeping the item's position. A field not in the list SHALL be appended as the list's last item. When the home note has no field list, a new list with the set fields SHALL be inserted after the title, separated from the title and from the following line by one blank line; with no title, it SHALL be inserted at the top of the note. The written key SHALL be lowercase. All other lines, including the note's line endings and trailing newline, SHALL be unchanged.

#### Scenario: Replace status, add archived
- **WHEN** `archived` is set to `2026-09-25` and `status` to `archived` in a home note with `- status: active` and `- tag: make-bread`
- **THEN** the list SHALL be `- status: archived`, `- tag: make-bread`, `- archived: 2026-09-25`

#### Scenario: Case-insensitive key
- **WHEN** `status` is set to `archived` in a home note with `- Status: paused`
- **THEN** that line SHALL become `- status: archived`

#### Scenario: No field list
- **WHEN** fields are set in a home note that is `# Make Bread`, a blank line, `Some notes.`
- **THEN** the note SHALL be `# Make Bread`, a blank line, the new field items, a blank line, `Some notes.`

#### Scenario: No title
- **WHEN** fields are set in a home note whose first line is `Some notes.` and which has no heading
- **THEN** the new field items SHALL be the first lines of the note, followed by a blank line and `Some notes.`
