## ADDED Requirements

### Requirement: Archiving a project writes its archive fields
When `meta-notes archive` (and so `:MetaNotesArchive`) archives a project (a note directly in `project/` or a folder directly in `project/`), it SHALL, before the move, set the fields `status: archived` and `archived: <today>` (as YYYY-MM-DD) in the project's home note, as defined by the `project-fields` capability. The fields mark the project archived whether or not it has moved. Archiving an area, a resource, or a note or folder nested inside a project SHALL NOT write any fields.

#### Scenario: Note project archived
- **WHEN** today is 2026-09-25 and the user archives `project/make-bread.md`, whose home note has `- status: active`
- **THEN** `archive/project/make-bread.md` SHALL have `- status: archived` and `- archived: 2026-09-25` in its field list

#### Scenario: Folder project archived
- **WHEN** the user archives `project/kitchen`, which has `Home.md`
- **THEN** `archive/project/kitchen/Home.md` SHALL have `status: archived` and today's `archived` date, and the folder's other notes SHALL be unchanged apart from link and header updates

#### Scenario: Area archived
- **WHEN** the user archives `area/health`
- **THEN** no note under `archive/area/health` SHALL gain `status` or `archived` fields

#### Scenario: Note nested in a project
- **WHEN** the user archives `project/kitchen/Tasks.md`
- **THEN** it SHALL be moved with no fields written

### Requirement: Folder project without a home note
Archiving a folder project with no `Home.md` SHALL still archive it, SHALL write no fields, and SHALL report a warning naming the folder. The command SHALL NOT fail because of the missing home note.

#### Scenario: Missing Home.md
- **WHEN** the user archives `project/trip`, which has no `Home.md`
- **THEN** `project/trip` SHALL be moved to `archive/project/trip`, no `Home.md` SHALL be created, and a warning that archive fields were not written SHALL be reported

### Requirement: Fields kept when the move fails
If the move fails after the fields were written, the fields SHALL stay written in the project's home note at its original path, and the error SHALL be reported as for any failed archive, saying the project was marked archived but not moved.

#### Scenario: Target already exists
- **WHEN** the user archives `project/make-bread.md` and `archive/project/make-bread.md` already exists
- **THEN** the command SHALL fail with an error, `project/make-bread.md` SHALL stay in place with `status: archived` and today's `archived` date, and the error SHALL say it was marked archived but not moved

#### Scenario: Batch item fails to move
- **WHEN** a wildcard batch includes a project whose move fails
- **THEN** that item SHALL be reported as failed with `fields_written` true, and the other items SHALL be archived

### Requirement: Field-write failure does not stop the move
If writing the home note's fields fails, the project SHALL still be moved and reported as archived, with a warning naming the home note and saying its fields were not written.

#### Scenario: Unwritable home note
- **WHEN** the project's home note cannot be written
- **THEN** the project SHALL be moved to `archive/project/`, reported as archived, and a warning SHALL name the home note

### Requirement: Archive result reports fields
Each item's JSON result, archived or failed, SHALL include `fields_written` (true when the archive fields were written) and `home` (the home note path when the item is a project with a home note, otherwise null; the archived path when the move succeeded, the original path when it failed). The text message for a project whose fields were written SHALL end with `(status: archived)`.

#### Scenario: JSON for a project
- **WHEN** the user runs `meta-notes archive project/make-bread --json`
- **THEN** the item SHALL have `fields_written` true and `home` `archive/project/make-bread.md`

#### Scenario: JSON for a resource
- **WHEN** the user runs `meta-notes archive resource/recipes --json`
- **THEN** the item SHALL have `fields_written` false and `home` null
