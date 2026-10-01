---
id: cpwr
title: task update can't change a task's text
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
---

# task update can't change a task's text

From the notes advisor (2026-10-01): `meta-notes task update` edits a
task's status, tags, dates and recurrence, but not its words. When the
human asked to reword a task in `project/zettel-migration/Home.md`, the
advisor had to hand-edit the line, which the skills' rule (edit notes only
through the CLI) is meant to avoid.

## Wanted

`task update --text {text}`: replace the task's description, the words
`task add` takes, and keep everything else on the line as it is: indent,
checkbox and status, tags, the 🛫/due/⏰/🔁/✅ fields and their order.
Same `--expect` guard and same one-line write as the other options; it
combines with them in one call (for example `--text ... --status x`).
Tags inside the old description are part of the words being replaced: a
tag the caller wants kept is in the new text, or added with `--add-tag`.
Empty text is an error.

## Done means

The option, its help in `:help meta-notes-cli-task-update` and the
conventions text the skills read, a spec, and unit tests (text only; with
dates and recurrence kept; combined with another option; empty text
rejected; --expect mismatch writes nothing). MINOR bump.
