## Why

`agent-prime` left the suggested `CLAUDE.md` for a notes root in
`docs/work-notes-claude.md`, a design-docs folder nobody would look in,
and `meta-notes init` only prints the one line to add. Setting up a new
root means finding that file by hand.

## What Changes

- Move `docs/work-notes-claude.md` to `templates/suggested-CLAUDE.md`,
  beside the other files init works from, and make its opening generic.
- When `CLAUDE.md` lacks the `prime` line (always the case on a first
  run), `meta-notes init` and `:MetaNotesInit` also give the suggested
  file's absolute path and the `cp` command to start from it.
- Init still never creates or edits `CLAUDE.md`.

## Capabilities

### New Capabilities

### Modified Capabilities
- `init`: the `missing` message points to the suggested `CLAUDE.md`

## Impact

- `templates/suggested-CLAUDE.md` (moved from `docs/`)
- `scripts/meta_notes/init.py`, `scripts/meta_notes/cli.py`,
  `autoload/meta_notes/notes.vim`: the message
- `test/unit/test_init.py`, `test/init.vader`
- `doc/meta-notes.txt`, `README.md`
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
