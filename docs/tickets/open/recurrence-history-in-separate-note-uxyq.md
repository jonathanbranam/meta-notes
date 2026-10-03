---
id: uxyq
title: Recurring tasks keep their history in a separate, linked note
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: []
see: [zqqb]
tasks: []
---

# Recurring tasks keep their history in a separate, linked note

The human, 2026-10-03 (relayed by the notes advisor). Completing a
recurring task leaves the done line in place and inserts the next
occurrence above it (task-update's recurring completion, like the Obsidian
Tasks plugin):

> fine for what it is, but after a couple months and years, it just is
> annoying as hell. I like having the history, but I don't want it in the
> same file... What I want to see in the main file... like the home
> maintenance file, I usually want to see the next time I need to do
> something and the previous time I did it. And that's all. And then I
> want to have a link to the history

followed in Obsidian or Vim. Example: the Zettel vault's
`Personal/Home Maintenance.md`, 289 lines, mostly done recurrences. The
notes advisor started `area/home/Maintenance.md` with current tasks only
and is holding the history back until this is designed.

## A starting design (for the human to confirm)

- Completing a recurring task inserts the next occurrence as today, and the
  main note keeps only the newest done line of that task, directly under
  the next one. The older done line moves to a history note.
- The history note sits beside the main note: `Maintenance History.md` for
  `Maintenance.md` (`[[area/home/Maintenance History]]`). It's created on
  first use, newest first, grouped under the task's text. The main note
  gets one link line to it if missing.
- A one-time command moves the existing done recurrences of a note into its
  history (for the Zettel note and the advisor's import).
- `tasks` and the time reports still read the history note as an ordinary
  note.

## Needs the human

The history note's name and place (beside the note, or under a `history/`
folder); one history note per note, or one per task; whether "previous time
I did it" is the done line itself or a `last done` date on the next line;
and whether the split applies to every recurring task or only notes that opt
in. Note the task-update spec's line-stability promise (only the target and
the inserted line change) changes for recurring completions.
