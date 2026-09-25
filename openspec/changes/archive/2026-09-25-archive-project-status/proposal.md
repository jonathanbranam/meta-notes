## Why

An archived project should say so in its own note, not only by where it
sits. The project model in `docs/planning-system.md` gives a project's home
note `status: archived` and an `archived: YYYY-MM-DD` field when it moves
to `archive/project/`. Writing those by hand, or leaving it to a skill,
means they get forgotten. `meta-notes archive` already does the move, so it
should write the fields too.

## Dependencies

None outstanding. The project model (home note, field list) is defined in
`docs/planning-system.md`. `project-brief` reads the same fields; whichever
change lands first adds the shared field parser.

## What Changes

- When `meta-notes archive` archives a project (a note or folder under
  `project/`), it also updates the project's home note: the note itself,
  or `Home.md` for a folder.
- In the field list (the first list after the home note's title), it sets
  `- status: archived`, replacing any existing `status` item, and sets
  `- archived: <today>`. Other items and the rest of the note are
  unchanged.
- A home note with no field list gets one after its title. A home note with
  no title gets one at the top of the note.
- A folder project with no `Home.md` is still archived, with a warning that
  no fields were written.
- Areas and resources are archived as before, with no fields.
- Each archived item's result (text and JSON) reports whether fields were
  written.

## Capabilities

### New Capabilities
- `project-fields`: the project home note and its `key: value` field list,
  shared with `project-brief`

### Modified Capabilities
- `archive`: `archive` writes the archive fields for projects

## Resolved Questions

- Fields are written before the move. If the move fails, the project
  stays marked archived and the error says so; a failed field write only
  warns and the move goes ahead (see design.md).
- Un-archiving is left to the user: `move` does not touch fields.

## Impact

- `scripts/meta_notes/ops.py`: field update in `archive_item` for projects
- `scripts/meta_notes/`: a project field parser and editor, shared with
  `project-brief`
- `test/unit/test_ops.py`: note and folder projects, existing and missing
  field lists, missing `Home.md`, areas unchanged
- `doc/meta-notes.txt`: `archive` reference
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
