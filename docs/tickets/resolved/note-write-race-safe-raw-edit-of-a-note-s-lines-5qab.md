---
id: 5qab
title: "note write: race-safe raw edit of a note's lines"
kind: feature
opened: 2026-10-05
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [5wam]
tasks: [mn-5qab]
closed: 2026-10-05T10:48:47Z
---

## The ask

For meta-notes-ui (ticket 5wam, its v1.3 eqqv): the UI edits a block of
a note as raw markdown and must write it through the CLI (UI rule
writes-through-the-cli), race-safe like every other write.

`meta-notes note write <file> --lines A..B --expect <old> --text <new>
[--json]`: replaces lines A..B (1-based, inclusive) with `--text` only if
they are exactly `--expect` now; otherwise refuses, printing the current
lines (exit non-zero; `--json` gives `{ok: false, current: ...}`). `--text`
may have more or fewer lines than the range; `--text ''` deletes them.
`--lines` omitted means the whole file, still with `--expect`. Also
`--create` for a file that doesn't exist (with `--expect ''`). Paths
confined to the root, as other commands. Trailing newline kept as is.
`--json` reports the new line range so the caller can keep editing.

Spec, pytest, `:help meta-notes-cli`, README command list. Minor version.
