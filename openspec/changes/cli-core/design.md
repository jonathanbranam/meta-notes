## Context

Today, `meta_notes#file_ops#MoveItem` shells out to `mv`, rewrites the
moved note's `# path` header in Vimscript, and calls `update_links.py` once
per moved path (each file, plus the folder itself). `Archive` and `Rename`
build on it. `scripts/update_links.py` already implements link rewriting in
Python. Task parsing lives in `scripts/tasks.py` and `scripts/find_tasks.py`,
which the daily-note templates call directly.

All paths are relative to Vim's current directory, which is assumed to be
the notes root. The vader tests create `project/`, `area/`, and `resource/`
in a temp directory, but not `plan/`.

The notes root is a git repo, committed by the user roughly once a day.

This change is a port. Anything that would change observable behavior is
out of scope, even where the current behavior is a known quirk.

## Goals / Non-Goals

**Goals:**
- One implementation of move, rename, and archive, callable from Vim, an
  agent, and a local server
- The existing task query available through the CLI
- Machine-readable output for every command
- Existing vader tests pass without modification

**Non-Goals:**
- New task syntax, filters, or fields (`find-tasks-enhancements`)
- Editing tasks (`task-update`) or project summaries (`project-brief`)
- Fixing link-rewrite quirks or reloading more buffers after a move
- `init` (`cli-init`) and time reports
- Replacing the Vim UI; Vim remains the authoring tool

## Decisions

### 1. Package layout and entry point

`scripts/meta_notes/` is a package with `cli.py` (argparse subcommands),
`ops.py` (move, rename, archive), and `query.py` (tasks). `bin/meta-notes`
runs `python3 -m meta_notes` with `scripts/` on `sys.path`, so the existing
flat imports (`from tasks import ...`) keep working. Existing scripts keep
their `main()` functions.

**Why not a single script:** the CLI will grow (task updates, project
briefs, init, dashboard support), and the existing scripts are already
split by concern.

### 2. Notes root resolution

In order: `--root`, then `META_NOTES_ROOT`, then walk up from the current
directory to the first directory containing `plan/`, `project/`, and
`area/`. Fail with a clear error if none is found. Work and personal roots
never interact.

The CLI changes into the root before operating, and paths in arguments and
output are relative to it. Vim always passes `--root` with its current
directory. That matches today's behavior, where everything is relative to
the current directory, and works in vader fixtures that have no `plan/`.

### 3. Output and errors

Human-readable by default. With `--json`, stdout carries exactly one JSON
object, on success and on failure. A failure is
`{"ok": false, "error": "..."}` with a non-zero exit, and warnings go in a
`warnings` array. Without `--json`, errors and warnings go to stderr.

**Why errors on stdout under `--json`:** Vim's `system()` merges stderr into
the captured output (`shellredir` is `>%s 2>&1`), so anything on stderr
would corrupt the JSON Vim parses.

Error messages are the ones Vimscript produces today (for example,
`Can only archive items from project/, area/, or resource/ folders`), because
vader tests match on them.

### 4. Move, rename, archive are ported as-is

`ops.move(src, dst)` reproduces `MoveItem`:
- a file source whose name ends in `.md` gets `.md` appended to the
  destination if missing
- an existing target file is an error
- parent directories are created
- folders move whole, including non-markdown files
- the move list is every `.md` file under the folder plus the folder itself
- a moved note's first line is rewritten only if it is exactly
  `# <old path without .md>`
- `update_links.update_all_links` runs for each entry in the move list, with
  `.` as the root after changing into the notes root

`ops.rename(src, new_name)` keeps the source's directory when `new_name`
has no `/`, and appends `.md` if missing. `ops.archive(path...)` keeps the
current rules: `.md` inference, only `project/`, `area/`, or `resource/`
sources, destination `archive/<path>`. Wildcards (`*`, `?`) are expanded by
the CLI, and each item is archived independently, with failures reported
per item and the rest continuing. `:MetaNotesArchive` passes its argument
through unexpanded.

The JSON result includes the `moves` list (`[[old, new], ...]`) and the
files whose links were rewritten.

**Known quirks, kept on purpose:** `update_links` doesn't match
`[[path|alias]]` or `[[path#heading]]`. It skips any path with a dot
directory, which is why the CLI passes `.` rather than an absolute root. It
rescans the tree once per moved file. Fixing these is a follow-up change.

### 5. Vim becomes a thin caller

`meta_notes#file_ops#MoveItem` keeps its signature and return dictionary
(`success`, `moves`, `error`), built from the CLI's JSON. `Archive` and
`Rename` keep their current buffer handling: `Rename` edits the new path
and wipes the old buffer, and `Archive` re-edits the current buffer when it
was the archived file. Messages shown to the user are unchanged. No other
buffers are reloaded, same as today.

### 6. Task query

`meta-notes tasks` accepts the same options as `find_tasks.py` (`--folder`,
`--due-on`, `--due-by`, `--due-between`, `--status`, `--format`,
`--condensed`) and prints identical text. With `--json`, it returns the same
tasks as a list of objects: `file`, `line`, `text`, `status`, `start`,
`due`, `completed`, and the report `category` when no filters are given.
`find_tasks.py` stays callable directly, because the daily-note templates
use it.

### 7. No git writes

The CLI never stages or commits. `move`, `rename`, and `archive` leave their
changes in the working tree for the user's own commit.

## Risks / Trade-offs

- **Vim latency:** each operation now spawns Python once instead of once per
  moved file for link updates, so it should be no slower.
- **Python version:** the scripts use `X | None` annotations, so they need
  Python 3.10 or newer. The shim uses `python3` from `PATH`, as Vim does
  today. On macOS, `/usr/bin/python3` is 3.9, so the shim fails early with
  a clear message on older versions.
- **Parity drift:** subtle differences from the Vimscript (such as path
  normalization or `.md` inference) would change behavior. Mitigated by
  keeping the vader tests unmodified and adding pytest cases that mirror
  them.

## Migration

1. Build the CLI with tests; keep Vimscript implementations in place.
2. Switch Vim commands to the CLI once vader tests pass against it.
3. Remove the Vimscript implementations.
