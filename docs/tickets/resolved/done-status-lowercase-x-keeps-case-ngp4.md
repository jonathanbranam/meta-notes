---
id: ngp4
title: Done is written as lowercase x, and an existing X is kept
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: [task-tree]
needs: []
see: [parent-done-only-when-all-subtasks-done-f3vg]
---

# Done is written as lowercase x, and an existing X is kept

The human, 2026-10-01: "an upper or lowercase X or x indicates 'done'.
Either is acceptable, but the CLI should always write a lowercase x. It
should preserve case to avoid unnecessary diffs."

v2.11.1 gets the parent rule right (a completed parent becomes `x`, a
parent already `X` stays `X`) and other edits keep `X`. Two cases are
wrong:

1. `task update --status X` on a task that isn't done writes `[X]`. It
   should write `[x]`: `X` and `x` are the same status on input, and the
   CLI writes lowercase.
2. `task update --status x` (or `X`) on a task that is already `X`
   rewrites it to `[x]`. It should leave the status character as it is:
   marking a done task done changes nothing.

`task replace`, `task notes` and `task add` write the caller's text as
given and aren't affected. Check any other place the CLI writes a done
status (for example a skill's `--status x` on a ceremony marker) follows
the same rule.

## Done means

The spec and `:help` for `--status` say both, with unit tests for the
two cases and for a done subtask given `--status X` not changing its
parent. PATCH bump.
