---
id: gmqp
title: time-block update, a race-safe command for Time Block Plan and Actual cells
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [docs/bug-report/time-block-request.md]
---

# time-block update: edit Time Block cells like task update edits task lines

Reported by the notes root's agent (the request is
`docs/bug-report/time-block-request.md`). While running `daily-plan` for
2026-09-30, the agent filled ~30 Plan cells in the `### Time Block` table
by hand with string replacement. Several rows came out one character too
wide, and a second pass had to re-pad the column. `task update` already
solves this for task lines: it edits by key, reformats for you, and refuses
when `--expect` doesn't match. The Time Block has no equivalent.
`checkin actual` writes Actual cells for today's note, but it can't write
Plan and has no `--expect`.

## What to build

```
meta-notes time-block update <file> --time 9:30am --plan 'text'
meta-notes time-block update <file> --time 9:30am --through 10:15am --plan 'text'
meta-notes time-block update <file> --time 9:30am --actual 'text' --expect 'old'
meta-notes time-block update <file> --time 7:00am --plan 'flight' --create
```

1. **Rows are found by time**, not line number. `--time` takes `9:30am` or
   `09:30`, the same forms `checkin` parses (reuse `checkin.parse_time` and
   `checkin.time_block_rows`).
2. **`--plan` and/or `--actual`.** At least one is required, and both may
   be given in one call. The text is written into the cell and padded to
   the column's width (reuse `checkin._cell`). `|` becomes `/` and
   newlines become spaces, as in `fill_actual`.
3. **`--through <time>`** covers every row from `--time` through it,
   inclusive, like `checkin actual --through`. One `--expect` applies to
   every covered cell. With no `--expect`, every covered cell must be
   empty. This is the request's "range" form, kept to one flag that
   already exists elsewhere in the CLI.
4. **`--expect`**: a non-empty target cell is only overwritten when
   `--expect` matches its current text exactly (compared after stripping).
   No `--expect` means "expect empty". If any cell doesn't match, nothing
   is written. The error names each mismatched row and gives its current
   text, which also appears in `--json` output, so the caller can re-read
   and retry. With both `--plan` and `--actual`, `--expect` applies to
   both cells. Callers that need different expectations make two calls.
5. **Clear failures, nothing written on any of them:**
   - no Time Block in the file;
   - "time slot not found" when `--time` (or `--through`) isn't a row and
     `--create` isn't given;
   - ragged table: the rows' cell widths differ for a column before the
     edit (report the rows);
   - text wider than the column: an error giving the column's width and
     the text's length. It doesn't truncate or widen the column. (This
     follows the request. If it proves annoying in practice, widening the
     whole column is a later change.)
6. **`--create`** adds a missing row, in time order and padded to the
   table's widths, with the label in the template's style (` 7:00am`, right
   aligned like ` 8:00am`). It applies only to `--time` without
   `--through`. If the row already exists, `--create` is a no-op and the
   update proceeds as normal.

Every command takes `--json`, and this one does too. Exit codes and error
output should look like `task update`'s.

## Where it goes

- A new module next to `checkin.py` (e.g. `scripts/meta_notes/time_block.py`)
  that shares checkin's parsing rather than copying it. Move helpers into
  it if that's cleaner.
- A new `time-block update` subcommand in `cli.py`.
- A new spec `design/specs/time-block-update.md` (rule `specs`).
- `doc/` help (a `meta-notes-cli-time-block` section) and the README's
  command list and examples.
- `skills/daily-plan/SKILL.md` fills the Plan with this command instead of
  hand-editing the table. `skills/checkin/SKILL.md` keeps `checkin actual`.
  `prime.md` mentions the command where it lists the Time Block.
- Unit tests in `test/unit/test_time_block.py` (rule `python-tests`).
- MINOR version bump (rule `versioning`).

## Related (notes root)

- `[[project/meta-notes/Port tasks and time_log features into meta-notes]]`
- `[[project/meta-notes/daily-plan skill - fill Time Block from meetings by default]]`
