---
id: cys2
title: "task add puts the task under ## Tasks, not after the Time Block"
kind: bug
opened: 2026-10-06
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

Reported by advisor (notes project, message m-0099, 2026-10-06): `meta-notes task add <daily note> ...` appended the task at the end of the file, after the Time Block table, instead of under `## Tasks`. The advisor moved two by hand (2026-10-06 Tue, 2026-10-08 Thu).

Today `task add` without `--line` appends at the end of the file (conventions: "appends the line (`--line <n>` inserts before line n)"). In a note with a `## Tasks` heading that is the wrong place.

## The ask

- Without `--line`, when the note has a `## Tasks` heading, insert the task at the end of that section: after its last non-blank line (after that task's notes and subtasks), before the next heading.
- No `## Tasks` heading: append at the end of the file, as now.
- `--line` keeps working as now.
- Update the conventions text (`scripts/meta_notes/conventions.md`, "Add a task with ...") and `:help` to match; patch version bump.

## Verify

Unit tests in `test/unit/test_task_update.py` (or wherever `task add` is tested): a daily note from the shipped template gets the task under `## Tasks`; an empty `## Tasks` section; a note without the heading still appends; `--line` unchanged.

Not in scope: other headings (`## Follow Up`); a `--section` option (YAGNI until asked).
