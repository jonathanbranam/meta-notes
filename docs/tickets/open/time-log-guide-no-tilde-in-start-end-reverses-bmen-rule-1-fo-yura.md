---
id: mn-yura
title: "Time Log guide: no tilde in start/end (reverses bmen rule 1 for the Time Log)"
kind: fix
created: 2026-10-25
created_by: external:orchestrator
repos: [meta-notes]
changes: []
specs: []
blocked_by: []
related: []
---

## The ask

The human, 2026-10-25 10:55 AM ET (relayed verbatim by aide, m-0112 on vesta-home):
"don't every use \"~\" in the time log, that isn't valid syntax for meta-notes"

`meta-notes prime` ("Editing the Time Log", `scripts/meta_notes/conventions.md:207`) says:
"A tilde before a time means approximately: `~9:00` for the start or end." That line, added by
bmen (resolved), led aide to write `~HH:MM` in Time Log start/end. This reverses bmen rule 1 for
the Time Log only. The Time Block tilde rule (`conventions.md:149`, `home ~9:20`) stays as it is.

## Widened scope (the human, 2026-10-25 11:04 AM ET, via aide, verbatim)

"I don't want ~ in the time log ever; it's just messy and IMO unnecessary; times may be
approximate, that is understood."

So nothing writes `~` to the Time Log. This reverses the write side of mn-3p28 (v2.26.7), which made
append accept and write `~HH:MM` because agents followed the guide line from mn-caa0 (bmen).
The ticket thread (aide's comment) has the background.

## Changes

- `time-log append` `--start` / `--end` / `--prev-start` / `--close-prev`, and `time-log update
  --text`: reject a leading `~` with a clear error; `--close-prev` never writes `~`.
- Drop the Time Log tilde from: the guide (`scripts/meta_notes/conventions.md:207`; start and end
  are plain `HH:MM`), `doc/meta-notes.txt`, `--help`, and the spec
  `design/specs/time-log-edit.md` (r-6bf7, s-295d, s-e683). Check `skills/` for the same advice.
- Update the tests mn-3p28 added to expect rejection.
- Patch release with a CHANGELOG entry.
- Read side (the human, 2026-10-25 11:06 AM ET, via aide, verbatim: "update the time report to
  accept the ~ but to issue a warning when it is found that this syntax is deprecated"): the time
  report keeps parsing `~` (`time_tracking._parse_entry_time`) and prints a deprecation warning
  naming the file and line for each one found.

## Verify

`meta-notes prime` and `--help` don't suggest `~` in the Time Log; `time-log append --start ~9:00`
fails with a clear error; old notes with `~` still report, with a deprecation warning naming file and line; spec check 0 errors; `just check` green.

## Model

Haiku (docs and a small validation).

## Out of scope

The Time Block tilde rules (bmen rules 1 and 2 for the Time Block) are unchanged.
