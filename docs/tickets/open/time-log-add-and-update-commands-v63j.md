---
id: v63j
title: time-log add and time-log update, race-safe commands for Time Log entries
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [time-block-update-command-gmqp, time-report-work-split-disagrees-286n]
---

# time-log add and time-log update: race-safe Time Log edits

Status: **design, waiting on the human's decisions** (below). Not queued.

## Why

The CLI can write the daily note's Time Block (`time-block update`) but not
its `### Log`. Agents edit the log by hand today. The human nearly always has
the daily note open in Vim and may change it between the agent reading the
file and writing it, so a hand edit can silently overwrite their change.
Like `task update` and `time-block update`, the CLI checks that what the
agent expects is still in the file and refuses otherwise.

The human, 2026-10-01: "we want to be safe in how these edits are applied,
and that's what the CLI will do for us."

## The entry format

```markdown
### Log

- Work
  * start: 09:45
  * end:   13:00
- Packed for the NY trip #2026-10-ny
  * start: 13:00
  * end:   14:00
  * any other indented lines (notes); no rule beyond start and end
```

An **entry** is the header line (`- <text and tags>`) plus every indented
line under it. The last entry may have no `end:` yet (an open entry).

## time-log add (append)

One entry per call, appended after the last entry.

```
meta-notes time-log add <file> \
  --prev '- Work' --prev-start 09:45 [--prev-open] \
  --text '- Packed for the NY trip #2026-10-ny' --start 13:00 [--end 14:00]
```

- **Guard**: `--prev` must equal the last entry's header line exactly and
  `--prev-start` its start time. `--prev-open` asserts the last entry has no
  end time; without it, the last entry must have one. Any mismatch fails and
  prints the current last entry. For an empty log, `--first` in place of the
  `--prev` options (fails if the log has entries).
- **New entry**: header `--text` (tags included), `* start:`, and `* end:`
  only with `--end`; aligned like the template (`end:   `).
- Validates times (HH:MM, or 9:30am like `time-block update`), and warns on a
  gap or overlap with the previous entry (see Warnings).

## time-log update (replace one entry)

Replace one whole entry, header and indented lines, with new text.

```
meta-notes time-log update <file> \
  --expect $'- Work\n  * start: 09:45\n  * end:   13:00' \
  --text   $'- Work #dev\n  * start: 09:45\n  * end:   12:30\n  * reviewed PRs'
```

- **Guard**: `--expect` must match one entry in `### Log` exactly (all of
  its lines). Zero matches fails and prints the entry the agent most likely
  meant (same header or same start), with the lines that differ marked.
  Two exact matches fails too (ask for more lines).
- **Replace**: the entry becomes `--text`. Header, start, end and notes
  lines can all change, lines can be added or dropped; no add or delete
  sub-operations.
- **Validation**: the new text must still be an entry: a `- ` header, a
  valid `start:`, and an `end:` that is valid if present. Invalid fails.
- Warns on a gap or overlap with the entries before and after.

## Warnings, not errors

A gap or overlap with a neighbouring entry is reported but the edit is
still written, in the time report's words (`*Gap of N min*`,
`*Overlap of N min*`) and in `--json` as `warnings`. Fixing a run of
wrong times takes one call per entry, and the log is inconsistent between
calls; that's expected. The human: "This [isn't] necessarily an error ...
if I made some mistakes in my time log, I may ask the agent to correct
them."

An end before its own start is an error (that entry alone is wrong).

## Suggestions for the human to decide

1. **Close the previous entry on add** (recommended). The usual add is
   "I switched to X at 13:00", which also means the open entry ended at
   13:00. `time-log add ... --prev-open --close-prev` writes the previous
   entry's `end:` as the new `--start` in the same guarded write, so the
   agent doesn't need a second command between which the human could edit.
2. **Find the entry to update by its text** (as above), not by line number
   (as `task update file:line` does). The expect text already pins it down,
   and agents don't need a line number from another command first. The cost:
   two identical entries can't be told apart, which shouldn't happen since
   their start times differ.
3. **One entry per call** for now, as the human said. Batch edits (fix three
   entries' times at once, warnings only at the end) can come later if
   needed.

## Also

- Conventions (`conventions.md`, "Editing the Time Block" or a new section):
  never hand-edit `### Log`; use these commands. Update the
  `daily-shutdown` skill, the one skill that mentions the log.
- `--json` for both, like `time-block update`.
- MINOR version bump (new commands).
