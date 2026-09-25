## Why

File operations (move, rename, archive) are orchestrated in Vimscript, so
only Vim can perform them. When an agent is asked to reorganize notes, it
can't, and suggests doing it by hand in Vim. The planned local dashboard has
the same problem.

The planning rituals in `docs/planning-system.md` depend on the agent being
able to read and change notes through the same code Vim uses. This change
builds that foundation by moving what exists today into a CLI, without
changing what it does. New behavior comes in follow-up changes
(`find-tasks-enhancements`, `task-update`, `project-brief`).

## What Changes

- Add a `meta-notes` CLI (Python, stdlib only) with notes root resolution,
  `--json` output on every command, and consistent error reporting.
- Move orchestration of move, rename, and archive from
  `autoload/meta_notes/file_ops.vim` into the CLI, with identical behavior:
  same path inference, header rewrite rule, link rewrite, wildcard archive,
  and error messages.
- The Vim commands (`:MetaNotesMoveItem`, `:MetaNotesRename`,
  `:MetaNotesArchive`) and `meta_notes#file_ops#MoveItem` keep their names,
  arguments, return values, and buffer handling, and call the CLI.
- Add `meta-notes tasks`, exposing the existing `find_tasks.py` options and
  output unchanged, plus `--json`.
- The CLI never stages or commits. It changes the working tree only.
- No change to task parsing, find_tasks filters, link matching, or which
  buffers Vim reloads. Known quirks are kept and listed in the design as
  follow-ups.

## Capabilities

### New Capabilities
- `cli`: The `meta-notes` command: root resolution, output and error
  conventions, move, rename, and archive through the CLI, and no git
  writes.
- `task-query`: `meta-notes tasks`, matching today's `find_tasks.py`
  filters and results.

### Modified Capabilities

*(none. `archive` requirements are unchanged; the implementation moves to
the CLI and the existing vader tests are the guard.)*

## Impact

- `scripts/meta_notes/`: new package with a `__main__` entry point;
  `find_tasks.py`, `tasks.py`, and `update_links.py` become modules it
  imports (their standalone entry points and the template calls to
  `scripts/find_tasks.py` keep working)
- `bin/meta-notes`: shell shim
- `autoload/meta_notes/file_ops.vim`, `plugin/meta_notes.vim`: call the CLI;
  header and link update logic is removed from Vimscript
- `test/unit/`: pytest coverage for every CLI command
- `test/*.vader`: existing archive and rename tests must pass unmodified
- `doc/meta-notes.txt`, `README.md`: CLI section and project structure
- Unblocks `cli-init`, `find-tasks-enhancements`, `task-update`, and
  `project-brief`
