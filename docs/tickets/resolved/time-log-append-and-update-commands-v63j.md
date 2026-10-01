---
id: v63j
title: time-log append and time-log update, race-safe commands for Time Log entries
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: [time-log-edit]
needs: []
see: [time-block-update-command-gmqp, time-report-work-split-disagrees-286n]
---

# time-log append and time-log update: race-safe Time Log edits

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

## Two commands

- **`time-log append`** adds one entry at the end of the log. It's the
  common case (the human hopes ~90% of calls): the last entry has a start
  and no end, and the new entry starts now.
- **`time-log update`** replaces a contiguous run of entries with zero or
  more entries: edit one, split one into several, merge several into one,
  or delete. It's a text replacement that knows what an entry is and
  validates the result.

Both take times as HH:MM or 9:30am, like `time-block update`, and both have
`--json`.

## time-log append

```
meta-notes time-log append <file> \
  --prev '- Work' --prev-start 09:45 --prev-open --close-prev \
  --text '- Packed for the NY trip #2026-10-ny' --start 13:00 [--end 14:00] \
  [--note 'packed the big suitcase' --note 'left the charger out']
```

- **Guard**: `--prev` must equal the last entry's header line exactly and
  `--prev-start` its start time. `--prev-open` asserts the last entry has no
  end; without it, the last entry must have one. Any mismatch fails and
  prints the current last entry. For an empty log, `--first` replaces the
  `--prev` options (fails if the log has entries).
- **`--close-prev`** (with `--prev-open`) writes the last entry's `end:` as
  the new `--start`, in the same guarded write, so switching activities is
  one call.
- **New entry**: header `--text` (tags included), `* start:`, `* end:` only
  with `--end` (aligned like the template, `end:   `), then one `* <note>`
  line per `--note`, in order. Extra lines go in the same call, so an
  append never needs an update after it.
- Warns on a gap or overlap with the previous entry (see Warnings).

## time-log update

```
meta-notes time-log update <file> \
  --expect $'- Work\n  * start: 09:45\n  * end:   13:00' \
  --text   $'- Work\n  * start: 09:45\n  * end:   11:00\n- Reviewed PRs #dev\n  * start: 11:00\n  * end:   13:00'
```

- **Guard**: `--expect` is the exact text of one or more contiguous whole
  entries in `### Log`: it starts at a header line and ends with the last
  line of an entry. Zero matches fails and prints the entries the agent
  most likely meant (same headers or start times), with the lines that
  differ marked. Two matches fails too (ask for more lines).
- **Replace**: the matched lines become `--text`, which is zero or more
  entries. An empty `--text` deletes the matched entries.
- **Validation**, for each entry in `--text`: a `- ` header, a valid
  `start:`, and an `end:` that is valid if present and not before its own
  start. Only the log's last entry may be open (no end). Any failure
  rejects the whole update; nothing is written.
- Warns on a gap or overlap between the new entries and with the entries
  before and after them.

## Warnings, not errors

A gap or overlap between neighbouring entries is reported, but the edit is
still written, in the time report's words (`*Gap of N min*`,
`*Overlap of N min*`) and in `--json` as `warnings`. Fixing a run of wrong
times can take several calls, and the log may be inconsistent between
them; that's expected. The human: "if I made some mistakes in my time log,
I may ask the agent to correct them."

## Decisions (the human, 2026-10-01)

- `append`, not `add`: it only ever appends.
- `--close-prev` on append, and `--note` lines on append so one call does it.
- update finds entries by their text, not a line number.
- update replaces a contiguous run of whole entries with zero or more
  entries: split, merge and delete all go through it.

## Also

- Conventions (`conventions.md`): never hand-edit `### Log`; use these
  commands. Update the `daily-shutdown` skill, the one skill that mentions
  the log.
- MINOR version bump (new commands).
