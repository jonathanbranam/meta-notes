## Why

Changing a task means hand-editing the line in whatever file it lives in.
The agent does this during reviews by rewriting lines itself, which is
error-prone (wrong line, broken emoji dates, missing ✅ date) and bypasses
the "one implementation" principle. The planned dashboard and Vim task
buffers need the same edits. One command that edits a task by file and line
gives all three callers the same, checked behavior.

## Dependencies

None outstanding. `cli-core` (package, root resolution, `--json` and error
conventions) and `find-tasks-enhancements` (the task model, due emoji, the
bare 📅 undated marker, `#later`, and tag aliases in `scripts/tags.py`) are
archived. The `file`, `line`, and `text` fields of `meta-notes tasks --json`
are the inputs for `<file>:<line> --expect <text>`.

## What Changes

- Add `meta-notes task update <file>:<line> --expect <text>`, which edits
  exactly one checkbox line. Any checkbox line can be edited, including a
  plain checkbox that queries ignore, so `--due undated` turns a checklist
  item into a task. A line with no checkbox is an error, not an edit.
- **Stale-line guard.** `--expect` is the line's text as last read. If the
  current line differs, nothing is written, and the command fails and reports
  the current text so the caller can re-query. There are no stable task IDs,
  because they would need new syntax on every line.
- Options, combinable in one call:
  - `--status <char>`: set the status character (space, `x`, `>`, `-`, `.`,
    `o`, `O`)
  - `--add-tag <tag>` / `--remove-tag <tag>`, repeatable (for example
    `#later`, `#next`). An added tag goes before the first 🛫, due, or ✅
    date emoji on the line, or at the end if there is none. Tags match the
    way queries match them, ignoring case and applying aliases, so
    `--remove-tag meeting` removes `#mtg`.
  - `--due <YYYY-MM-DD|undated|none>`: set the due date, make the due emoji
    bare, or remove it. A line's existing due emoji (📅, 📆, or 🗓) is
    kept. A new due emoji, dated or bare, is 📅.
  - `--start <YYYY-MM-DD|none>`: set or remove `🛫`
- Marking a task done appends `✅ <today>` only when the line has no
  completion date and today isn't its due date. Queries already use the due
  date for a completed task without ✅, so a task done on its due date needs
  no second date. `--no-completed` skips adding it. Any other status
  removes ✅, including canceled (`-`): a canceled task was not completed.
- Changing a date doesn't reschedule a task. `--due` and `--start` edit
  the task where it lives. `>` (rescheduled) is for a task copy that was
  planned but not done where it is, such as a task copied into a daily note
  and then moved to another note. Like canceled, it means "never done
  here", so the new date goes on the copy and `>` needs no `--due`.
  `--status '>'` only sets the character. There is no command that copies
  a task to another note; the caller writes any copy.
- Removing a line's last date marker (`--due none` or `--start none`) is
  allowed, with a warning that the line is no longer a task.
- The result (text or JSON) includes the old and new line text.

## Capabilities

### New Capabilities
- `task-update`: guarded single-line task edits (status, tags, dates) and
  completion-date stamping.

### Modified Capabilities

*(none)*

## Impact

- `scripts/meta_notes/`: new `task update` subcommand and a task-line
  editing module built on `scripts/tasks.py` parsing
- `test/unit/`: tests for each option, combined options, the expect
  mismatch, non-checkbox lines, and ✅ stamping and removal
- `skills/project-review/SKILL.md`: step 7 switches from direct edits to
  `meta-notes task update`
- `doc/meta-notes.txt`: command reference; `README.md`: Command Line
  examples
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
- Enables a later change for Vim task-buffer mappings and dashboard status
  changes
