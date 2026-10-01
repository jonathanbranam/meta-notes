---
id: f3vg
title: A parent task is marked done only when every subtask is done
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: [task-tree]
needs: []
see: [task-trees-notes-and-subtasks-m2at]
---

# A parent task is marked done only when every subtask is done

v2.11.0 sets an ancestor's partial status as bullets.vim does with the
markers ` .oOX`: `ceil(4 * checked / subtasks)`. That reaches `X` before
every subtask is done (7 of 8 gives `ceil(3.5) = 4`), and meta-notes counts
`X` as done, so the parent leaves the open-task queries while a subtask is
still open.

The human, 2026-10-01: "I hate that bullets behavior. ... A task should
never be marked off until every single subtask is done." (They work around
it in Vim at work with many repeated markers, and may replace bullets.vim;
meta-notes shouldn't copy bullets.vim's rule.)

## The rule

For an ancestor with `subtasks` direct subtasks, of which `checked` are
`x` or `X`:

- none checked: ` `
- all checked: `x`, lowercase (the human, 2026-10-01: "I prefer lowercase
  \"x\""); an ancestor already `X` stays `X`
- otherwise `.`, `o` or `O` by thirds: `.` up to 1/3, `o` up to 2/3, `O`
  above 2/3 (the character at `ceil(3 * checked / subtasks)` of `.oO`,
  1-based). Never `x` or `X`.

Everything else in the task-tree spec stays: only the status character
changes, nested ancestors nearest first, `ancestors` in `--json`.

## Done means

The spec (`task-tree`), `:help` (drop "This is what bullets.vim does"
and the 7/8 note), the conventions text if it states the rule, and unit
tests at each boundary, including 7 of 8 giving `O` and 1 of 3 giving `.`.
PATCH bump.
