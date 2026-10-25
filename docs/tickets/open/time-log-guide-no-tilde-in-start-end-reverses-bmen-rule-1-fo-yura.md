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

## Changes

- `scripts/meta_notes/conventions.md`, "Editing the Time Log": drop the tilde line; say start and
  end are plain `HH:MM`, never with `~` (an approximate time is just written as the best guess).
- Check `skills/` and other docs for the same Time Log tilde advice and drop it there too.
- If `meta-notes time-log append` / `update` currently accept `~` in `--start` / `--end` /
  `--prev-start`, make them reject it with a clear error. If they already reject it, no code change.
- Tests that pin the conventions text; patch release with CHANGELOG entry.

## Verify

`meta-notes prime` no longer suggests `~` in the Time Log; `just check` green.

## Model

Haiku (docs and a small validation).

## Out of scope

The Time Block tilde rules (bmen rules 1 and 2 for the Time Block) are unchanged.
