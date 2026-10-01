---
id: m2at
title: Tasks as trees, with their notes and subtasks
opened: 2026-10-01
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [task-update-text-option-cpwr]
---

# Tasks as trees, with their notes and subtasks

Today every checkbox line is a task of its own: the lines under it aren't
connected to it. The human, 2026-10-01, on how tasks are actually written:

> any indented lines below it are part of the task description itself. But
> that's only true if those lines are not tasks of their own. ... usually
> it'll be the task line and then some notes, and those are all part of the
> task definition itself and should be kind of treated as one thing. But
> then when there's subtasks, generally there's the main task and then
> comments on the main task. And then the subtasks start in a list below
> that. And if the subtasks have their own comments, those will be nested
> more deeply within that. ... I usually don't nest more than two deep ...
> But occasionally, I will.

```markdown
- [o] main task 📅 2026-10-08
  * a note on the main task
  * another note
  - [x] first subtask
    * a note on the first subtask
  - [ ] second subtask 📅 2026-10-06
```

## The model

- A **task** is a checkbox line plus its **notes**: the indented lines under
  it that aren't checkbox lines, up to the next line indented no deeper than
  the task. Deeper non-checkbox lines belong to the nearest checkbox line
  above them with a smaller indent, so a subtask's notes are its own, not
  the parent's.
- A **subtask** is a checkbox line indented under another task; a subtask
  can have its own notes and subtasks, to any depth (usually two or fewer).
- **Dates aren't inherited** (the human's decision). Either the parent or
  the subtasks may be scheduled, and often only one of them is. Each line
  keeps its own dates; queries match each line on its own and report its
  parent as context.
- **Partial completion follows bullets.vim** (the human's decision), the
  plugin that sets it in Vim today, with the human's markers ` .oOX`:
  after a subtask's status changes through the CLI, its parent's status
  becomes `markers[ceil(4 * checked / subtasks)]`, where only `x`/`X`
  count as checked. So none is ` `, up to 1/4 is `.`, up to 1/2 is `o`, up
  to 3/4 is `O`, and all is `X`. It goes on up the tree to each ancestor.
  Like the plugin, this changes only the status character (no ✅ date, no
  next occurrence for a recurring parent).

## Wanted

Reading and writing, at any node of the tree: one task with its notes, or
a whole subtree (the human: "allow only reading or writing to a subtask or
an entire task tree anywhere in the tree").

- **Read**: the task parser builds the tree. `tasks --json` reports each
  task's notes, parent and subtasks; a command shows one task by
  `{file}:{line}`, either the node alone (line plus notes) or its whole
  subtree.
- **Write**, all with the `--expect` guard and one write, like `task
  update` and `time-log update`: replace a task's notes; add a subtask
  (after the task's notes and existing subtasks); replace a node or a
  whole subtree with new text. Any status change to a subtask through the
  CLI updates its ancestors' partial status as above.
- The spec settles the command names and output shapes, in the style of
  `task update` and `time-log update`.

## Done means

Specs, `:help` and the conventions text the skills read, and unit tests
that cover: notes vs subtasks; a subtask's notes not counted as its
parent's; deeper nesting; a note after the subtasks; reading and writing a
node and a subtree; partial status at each threshold, and up two levels;
`--expect` mismatch writes nothing. Existing query results stay the same
apart from the added fields. MINOR bump (or two, if split into read then
write).
