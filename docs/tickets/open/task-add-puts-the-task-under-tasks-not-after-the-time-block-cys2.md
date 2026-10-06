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
tasks: [mn-cys2]
---

## The ask

Reported by advisor (notes project, message m-0099, 2026-10-06): `meta-notes task add <daily note> ...` appended the task at the end of the file, after the Time Block table, instead of under `## Tasks`. The advisor moved two by hand (2026-10-06 Tue, 2026-10-08 Thu).

Today `task add` without `--line` appends at the end of the file (conventions: "appends the line (`--line <n>` inserts before line n)"). In a note with a `## Tasks` heading that is the wrong place.

## The ask

- Without `--line`, when the note has a `## Tasks` heading, insert the task at the end of that section: after its last non-blank line (after that task's notes and subtasks), before the next heading.
- No `## Tasks` heading: put the task at the top of the file, below the H1 title after a blank line (the human, via advisor, 2026-10-06: "It should look for a header called Tasks if that exists it should add tasks there. If it doesn't exist and no line number, tasks should go at the top of the file below the H1 file header after a blank space."). A note with no H1: the top of the file, after any frontmatter.
- `--line` keeps working as now.
- Update the conventions text (`scripts/meta_notes/conventions.md`, "Add a task with ...") and `:help` to match; patch version bump.

## Verify

Unit tests in `test/unit/test_task_update.py` (or wherever `task add` is tested): a daily note from the shipped template gets the task under `## Tasks`; an empty `## Tasks` section; a note without the heading gets it below the H1 and a blank line; `--line` unchanged.

Not in scope: other headings (`## Follow Up`); a `--section` option (YAGNI until asked).

## Also: the done stamp's due-today exception (added 2026-10-06)

From the human, via advisor (m-0101): "The behavior with the done stamp is intended - the docs need to be clarifies and or role rules". `scripts/meta_notes/conventions.md` line 13 says flatly "A done task gets `✅ YYYY-MM-DD`" (printed by `prime` and `conventions`), so the advisor read it as a bug. Make that sentence carry the exception the `--status x` paragraph (line 136) already states: no `✅` when the task is due today (its due date already records the day), unless it recurs. Check skills/ and doc/meta-notes.txt for any other flat statement. Same commit and version bump as the task add fix.
