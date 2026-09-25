## Context

`ops.archive_item` resolves a path, checks it is under `project/`, `area/`,
or `resource/`, and calls `move`, which rewrites the `# <path>` header and
wiki-links. `cli.cmd_archive` turns each `ArchiveItem` into text and JSON;
warnings go to `Output.warnings`, which `:MetaNotesArchive` already echoes
through `meta_notes#cli`. No code reads project fields yet: `project-brief`
and `planning-skills` (`meta-notes projects`) both plan to share a parser,
and whichever lands first creates it. This change lands first.

## Goals / Non-Goals

**Goals:**
- One module, `scripts/meta_notes/project.py`, that finds a project's home
  note and reads and sets its fields, for `archive`, `project brief`, and
  `projects` to share.
- `archive` writes `status: archived` and `archived: <today>` for projects.

**Non-Goals:**
- Un-archiving. Moving a project out of `archive/` with `move` leaves its
  fields alone; the user resets `status` by hand.
- Writing fields from any other command, or a `meta-notes project set`
  command.
- Reading tags or tasks; that's `project-brief`.

## Decisions

### Write fields before the move

`archive_item` resolves the project, edits its home note in place, then
calls `move`. Archiving is the decision; the fields record it, and the
move is where the project is filed. So a failed move leaves the project
marked archived in `project/`, and the error says so: the user fixes the
move (usually an existing target) and reruns, and the rerun rewrites the
same fields. A failed field write only warns; the move still happens.

The edit never touches the title line, so `move`'s `# <path>` header
rewrite still sees the original first line.

*Alternative:* write after the move, so a failed move leaves the note
untouched. Rejected: an archived project should say so even when it could
not be filed.

### Projects are only top-level items of `project/`

`project.project_for(path)` returns the project for `project/<name>.md` or
`project/<name>`, and None for anything deeper. Wildcard batches like
`project/batch/*.md` archive notes inside a folder project, not projects,
so they get no fields. This matches how `meta-notes projects` lists
projects.

### Line-based parser, no markdown library

`project.py` reads the note as lines and finds: the title (first line
starting with `#`), then the first list block after it (consecutive lines
starting with `- ` or `* `, ignoring blank lines before it) that contains a
field item, stopping at the next heading. A field item matches
`^[-*] ([A-Za-z0-9_-]+):\s*(.*)$` and is not a checkbox. It returns the
fields as a dict with lowercase keys plus the line span of the list, so
the setter can edit in place. Fenced code is not special-cased: a title
followed by a code block with `- key: value` lines is rare in a home note.

`set_fields(path, fields)` reads bytes, splits keeping line endings,
edits, and writes back, the same way `_update_header` preserves content.
New lines use the line ending of the note's first line.

### Reporting

`ArchiveItem` gains `fields_written: bool` and `home: str | None`. A
missing `Home.md` or a failed write adds a warning, which `cmd_archive`
forwards. Warnings are collected before the move, so they're held on the
`ArchiveItem` rather than the `MoveResult`, and a failed item carries
`fields_written` too. A single-path move failure re-raises `OpError`
with "marked archived but not moved" added to the message. The text
message gets ` (status: archived)` appended when fields were written.

### Today

`archive_item` and `archive` take an optional `today: date` (default
`date.today()`), the same pattern as `note.py` and `task_update.py`, so
tests pass a fixed date.

## Risks / Trade-offs

- [Existing archive tests assert exact note contents of archived projects]
  → Update those assertions (unit and vader) to include the new field list,
  or use area/resource fixtures where the test is about moving.
- [A home note whose first list is a plain bulleted list with a colon, e.g.
  `- Note: call first`] → It is read as a field list and gets
  `status`/`archived` appended to it. Acceptable: the project model puts
  fields first, and the edit is visible in the diff.
- [Parser semantics diverge from `projects`/`project brief`] → Both reuse
  `project.py`; the `project-fields` spec is the one definition.
