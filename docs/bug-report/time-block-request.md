# project/meta-notes/Add a time-block cell update command to meta-notes

For the meta-notes plugin maintainer.

## Problem

The `### Time Block` table (in every daily note) has two editable
columns, Plan and Actual, one row per 15-minute slot. `meta-notes` has a
precise, race-safe way to edit task lines (`meta-notes task update
<file>:<line> --expect '<text>' ...`), but no equivalent for Time Block
cells. Today the only way to fill in Plan or Actual is to hand-edit the
Markdown table with a text-editing tool (e.g. an `Edit`/`sed`-style
string replacement), which has to reproduce the table's exact column
widths by counting characters.

While running `daily-plan` for 2026-09-30, filling in ~30 rows of the
Plan column by hand produced a table where most rows were padded to 38
characters but several (any cell close to the column's max width) came
out at 39, because a trailing-space-vs-none miscount is easy to make
across many rows edited in one pass. Detecting and fixing this required
a second, separate script pass to re-pad every Plan cell to a uniform
width. This is exactly the kind of mechanical, error-prone editing that
`task update` already solves for task lines.

## Requested feature

A command like:

```
meta-notes time-block update <file> --time 9:30am --plan 'text' --expect ''
meta-notes time-block update <file> --time 9:30am --actual 'text' --expect ''
```

that:

1. Finds the row by its `Time` column value (e.g. `9:30am`), not by
   line number — row position can shift if earlier rows change, and the
   time value is already the natural unique key within one table.
2. Writes the given text into the Plan or Actual cell (whichever flag is
   given; allow both in one call, e.g. `--plan '...' --actual '...'`),
   re-padding that cell to the table's existing column width
   automatically, the same way `task update` already reformats a task
   line rather than requiring the caller to preserve spacing by hand.
3. Errors clearly if the time isn't found, if the table's columns are
   ragged (inconsistent widths) before the edit, or if the requested
   text is wider than the column (rather than silently truncating or
   corrupting alignment).
4. Optionally supports a `--range <start> <end>` or comma-separated
   list of times to set the same text across multiple contiguous rows
   in one call, since a single block of work commonly spans several
   15-minute rows (this was the common case in practice — most edits
   were "set this same text across N consecutive rows"). This is
   expected to combine awkwardly with the `--expect` requirement below
   in some cases (e.g. a range spanning rows with different existing
   text can't have one single expected value) — that's fine, the range
   form can just require every covered cell to currently be empty, or
   require a per-row expect list, whichever the maintainer finds
   cleanest.
5. Rejects the update if the target cell already contains non-empty
   text, *unless* the caller passes `--expect '<text>'` and that text
   matches the cell's current contents exactly (mirroring `task
   update`'s existing `--expect` behavior for task lines). This matters
   because the human user may hand-edit the Time Block (e.g. filling in
   Actual as they work) while an agent is mid-thought about a Plan
   update from stale context; without this check the agent would
   silently clobber the user's concurrent edit. On rejection, the error
   should include the cell's actual current text so the caller can
   decide whether to re-read and retry.
6. Supports an explicit `--create` (or similar) flag to add a time slot
   row that doesn't currently exist in the table — e.g. an event before
   8:00am or after 6:00pm, outside the template's normal range. Without
   this flag, targeting a `--time` that isn't already a row in the table
   should fail with a clear "time slot not found" error rather than
   silently doing nothing or guessing where to insert it; the point is
   that missing-row and wrong-row-content are two distinct, clearly
   reported failure modes.

## Why this belongs in the plugin, not this repo

Time Block table format and column widths are defined by the plugin's
daily note template and read by its own tooling (time tracking parsing
already parses this table); a local workaround here would just be
another hand-rolled script duplicating logic that belongs next to the
existing `task update` command.

## Related

- [[project/meta-notes/Port tasks and time_log features into meta-notes]]
- [[project/meta-notes/daily-plan skill - fill Time Block from meetings by default]]

