---
id: kkrj
title: "time-block replace: rewrite a range of Time Block rows in one call"
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [gmqp]
tasks: [mn-6523]
---

# time-block replace: rewrite a range of Time Block rows in one call

The human, 2026-10-03, approved (relayed by the notes advisor). Reordering
a Saturday morning took 5 `time-block update` calls, each with `--expect`,
plus 2 `task update --time` calls; one failed on the Actual column's width
and stopped the batch half done. In their words:

> You should be able to rewrite a whole section of the time block in one go
> and with the consistency checks that we've already implemented and also
> the CLI should validate the column counts and that column layout should
> follow whatever is in that plan file itself. It shouldn't be hard-coded in
> the CLI... each computer may have a template with the planned and actual
> columns being slightly different sizes.

Same family as `task replace` (a task with its subtree) and
`time-log update` (a run of entries).

## Change

1. **`meta-notes time-block replace <file> --time A --through B --expect
   "$old" --text "$new"`.** `$old` is the table rows from A through B as
   the agent read them (from the note or `--json` output). It is compared
   cell by cell, stripped, so padding never has to match; any difference
   fails and lists each row, column and its current text (`current` with
   `--json`), like `time-block update`'s expect guard. `$new` is the new
   rows, padding optional: each `| time | plan | actual |` with the
   header's number of cells. The CLI pads every cell to the file's widths
   and right-aligns the labels like `--create` does.
2. **Rows in `$new`:** every time from the range must still be there (no
   deleting rows); new times inside A..B are allowed and go in time order.
   Times outside A..B, a wrong cell count, a duplicate time, or text wider
   than its column fail with a message naming the row.
3. **All or nothing.** Every check runs before anything is written; one
   failure writes nothing.
4. **Column layout from the file.** Find Plan and Actual by the table's
   header names (case-insensitive), not `COLUMNS = {"plan": 2, "actual":
   3}` in `time_block.py`; widths already come from the file. Apply the
   same lookup to `time-block update` and `checkin`'s Actual writes. A
   table without both headers fails, naming the headers it found.
5. `conventions.md`, `prime.md` and the `daily-plan` skill: name `replace`
   for rewriting several rows; `update` stays for one cell or a range set to
   the same text.

Out of scope: warning on Markdown markup inside cells (the human asked for
none there; it's in the notes root's CLAUDE.md, and the agent follows it).

## Done means

Spec `time-block-update` gains the `replace` requirements (or a sibling
spec); `:help` and README examples; unit tests for a reorder that adds a
row, a stale `--expect` (padding-only differences pass), a too-wide cell
leaving the file unchanged, a wrong cell count, a deleted row, a
time outside the range, and a template whose columns are in another order
and width. MINOR bump.
