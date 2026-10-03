---
id: 5rhr
title: time-log update reports wrote 1 entry for a multi-entry replace
kind: bug
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [v63j]
tasks: [mn-e2d5]
closed: 2026-10-03T13:59:37Z
---

# time-log update reports "wrote 1 entry" for a multi-entry replace

Reported 2026-10-03 by the notes advisor: `meta-notes time-log update`
replacing 7 entries printed `wrote 1 entry`; the file was right.

Cause: `time_log.update` returns `written` as one item holding the whole
replacement text (`scripts/meta_notes/time_log.py`, end of `update`), and
`cli.py` prints `len(result.written)` entries.

## Change

`written` gets one item per new entry (`line`, `text`), so the text output
counts entries and `--json` lists each. Deleting (empty `--text`) still
reports `deleted entries`; if the spec defines `written`, update it.

## Done means

Unit test: replacing one entry with three reports `wrote 3 entries` and
three `written` items with their line numbers. PATCH bump.
