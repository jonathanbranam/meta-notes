## Why

Changing a task means hand-editing the line in whatever file it lives in.
The agent does this during reviews by rewriting lines itself, which is
error-prone (wrong line, broken emoji dates, missing ✅ date) and bypasses
the "one implementation" principle. The planned dashboard and Vim task
buffers need the same edits. One command that edits a task by file and line
gives all three callers the same, checked behavior.

## Dependencies

**Depends on `cli-core`** (package, root resolution, `--json` and error
conventions). **Should land after `find-tasks-enhancements`**, which defines
the bare 📆 undated marker and `#later` that this command writes.

## What Changes

- Add `meta-notes task update <file>:<line> --expect <text>`, which edits
  exactly one task line.
- **Stale-line guard.** `--expect` is the line's text as last read. If the
  current line differs, nothing is written, and the command fails and reports
  the current text so the caller can re-query. There are no stable task IDs,
  because they would need new syntax on every line.
- Options, combinable in one call:
  - `--status <char>`: set the status character (space, `x`, `>`, `-`, `.`,
    `o`, `O`)
  - `--add-tag <tag>` / `--remove-tag <tag>`, repeatable (for example
    `#later`, `#next`)
  - `--due <YYYY-MM-DD|undated|none>`: set the 📆 date, make it a bare 📆,
    or remove it
  - `--start <YYYY-MM-DD|none>`: set or remove `🛫`
- Marking a task done appends `✅ <today>` when the line has no completion
  date. Reopening a task removes it.
- The result (text or JSON) includes the old and new line text.
- A line that isn't a task is an error, not an edit.

## Capabilities

### New Capabilities
- `task-update`: guarded single-line task edits (status, tags, dates) and
  completion-date stamping.

### Modified Capabilities

*(none)*

## Open Questions

- Stamp ✅ on cancel (`-`) too? The project-review skill does; the planning
  doc only mentions done.
- Warn when the edited line exceeds 80 columns, which the planning doc asks
  for (emoji count as two)?
- Where tags go when added: end of line, or before the date emoji?
- Should rescheduling (`>`) require a new `--due`?

## Impact

- `scripts/meta_notes/`: new `task update` subcommand and a task-line
  editing module built on `scripts/tasks.py` parsing
- `test/unit/`: tests for each option, combined options, the expect
  mismatch, non-task lines, and ✅ stamping and removal
- `skills/project-review/SKILL.md`: step 7 switches from direct edits to
  `meta-notes task update`
- `doc/meta-notes.txt`: command reference
- Enables a later change for Vim task-buffer mappings and dashboard status
  changes
