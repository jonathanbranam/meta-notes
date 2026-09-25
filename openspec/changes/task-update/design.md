## Context

The CLI (`scripts/meta_notes/cli.py`) dispatches subcommands to modules in
`scripts/meta_notes/` (`ops.py`, `query.py`, `note.py`), each raising its
own error type that `cli.py` turns into a `CliError`. `note` already uses a
second level of subcommands (`note daily`, `note new`), and `archive` shows
how a handler returns an `Output` with both `error` and `data`, so a failure
can carry extra JSON fields.

Task parsing lives in `scripts/tasks.py`. The checkbox regex is inline in
`find_tasks_in_file`, as is the rule that a checkbox is a task only with a
due emoji or a `🛫` date. `DUE_EMOJIS` and `_char_to_status` are there too.
Tag names, aliases, and `canonical_tag` are in `scripts/tags.py`. The due
pattern allows an emoji variation selector (`️`) after the emoji; the
`🛫` and `✅` patterns don't.

See proposal.md for motivation and specs/task-update/spec.md for behavior.

## Goals / Non-Goals

**Goals:**
- One line editor that every caller (skills, Vim, dashboard) goes through.
- The same checkbox, task, and tag rules as `meta-notes tasks`, from the
  same code, so an edit and the next query can't disagree.
- Edits that touch only the markers they change, leaving the rest of the
  line as the user wrote it.

**Non-Goals:**
- Copying or moving tasks between notes (rescheduling makes no copy).
- Backdating the completion date. ✅ is always today; `--no-completed`
  skips it.
- Editing task text, or several lines in one call.
- Vim mappings and dashboard actions (a later change).

## Decisions

### Module: `scripts/meta_notes/task_update.py`

It holds `update(path, line_no, expect, *, status, add_tags, remove_tags,
due, start, no_completed, today) -> UpdateResult` and raises
`TaskUpdateError` (with an optional `current` line for a mismatch). The
result has `old`, `new`, `changed`, and `warnings`. `today` defaults to
`date.today()` and lets tests fix the date. The name avoids confusion with
`scripts/tasks.py` and its `test_tasks.py`.

*Alternative:* a top-level `scripts/task_update.py` beside `tasks.py`. No
standalone script or template needs it, so it belongs with the other CLI
command modules.

### Shared rules come from `tasks.py` and `tags.py`

`tasks.py` gains a module-level `CHECKBOX_PATTERN` and `is_task(text)` (a
due emoji, or `🛫` with a valid date), and `find_tasks_in_file` uses both.
`task_update` uses them to reject non-checkbox lines and to warn when an
edit stops a line being a task. Tag matching uses `tags.TAG_PATTERN` and
`canonical_tag`, compared lowercase, so `--remove-tag meeting` finds
`#mtg` exactly as `--tag meeting` does in a query.

### Edit the line as marker tokens, in a fixed order

The editor never re-renders the line from a parsed `Task`. It finds marker
tokens with regexes and replaces or removes just those spans:

- a date marker is the emoji, an optional `️`, optional whitespace,
  and an optional `\d{4}-\d{2}-\d{2}`. The date is matched by shape, so an
  invalid date such as `2026-02-30` after an emoji is still replaced or
  removed with it.
- a tag is `tags.TAG_PATTERN` (`#` plus `[\w-]+`), matched anywhere in
  the line, exactly as queries match it.

Edits apply in this order: remove tags, due, start, status and ✅, add
tags. The due edit comes before the ✅ decision because the rule compares
today with the due date after this call's edits. Tags are added last so
their position ("before the first date emoji") sees the final markers.

Removing a token removes the whitespace before it. When the token directly
follows the checkbox (`- [ ] #mtg prep`), it removes the whitespace after
it instead. No other spacing in the line is normalized, so hand alignment
survives. New markers are inserted with single spaces, and new date markers
follow the order `🛫`, due, `✅` relative to whatever markers the line
already has.

*Alternative:* parse to a `Task` and write the line back out in a canonical
form. That's simpler to code, but it would reorder markers and rewrite
spacing and emoji on every edit, which is the kind of unrequested change
that makes a diff hard to review.

### File I/O keeps everything but the line

The file is read with `newline=''` and split with `splitlines(keepends=True)`,
so each line keeps its own ending (LF or CRLF) and the last line keeps its
newline or lack of one. Only the content before the target line's ending is
replaced. The file is written in place, as `ops.py` does, and not at all
when the new text equals the old. The comparison with `--expect` uses
`rstrip()` on both, matching the `text` field of `meta-notes tasks --json`.

### CLI shape

`task` is a subcommand group with one kind, `update`, built the same way as
`note`. The target is split with `rpartition(':')`, and its path goes
through `to_root_relative` like the file operations. Values are checked in
`cli.py` before the file is read: `--status` with `choices`, `--due` and
`--start` against `YYYY-MM-DD` (regex, then `date.fromisoformat`, since
`fromisoformat` alone accepts other forms) or the keywords, tag names
against `[\w-]+`, and a tag given to both `--add-tag` and `--remove-tag`.
A mismatch returns `Output(error=..., data={"current": ...})`, so JSON
callers get the current line without parsing the message.

*Alternative:* `meta-notes tasks update`. `tasks` is a query whose options
sit directly under it, and adding a subcommand there would mix the two
argument sets.

## Risks / Trade-offs

- [The file changes between the `--expect` check and the write] → Not
  guarded. The window is milliseconds and the callers are one person's
  tools. A later Vim caller must `:checktime` the edited buffer.
- [A Vim buffer has unsaved edits to the same file] → The CLI writes the
  file on disk; Vim will offer to reload. Vim mappings (a later change)
  should write or refuse modified buffers before calling.
- [A tag-shaped fragment such as `[[note#heading]]` is treated as a tag]
  → Same as queries, which read it as a tag too. Changing that belongs in
  `tags.py`, for both.
- [`✅` dates depend on the day the command runs] → A shutdown run after
  midnight stamps the next day. `--no-completed` avoids a wrong date, and
  backdating can be added later without changing this behavior.

## Migration Plan

No note content changes. Ship with a MINOR version bump on archive. The
project-review skill switches its step 7 edits to `meta-notes task update`
in the same change; older copies of the skill keep working because they
edit lines directly.
