# meta-notes conventions

The syntax and editing rules every skill and agent follows in a meta-notes
notes root. Run `meta-notes` from anywhere inside the root; paths are
relative to it.

## Tasks

A checkbox line is `- [c] text`, with `-`, `*`, or `+` and one status
character `c`. It is a **task** only when it has a due date
(`📅 YYYY-MM-DD`, or a bare `📅` for undated) or a start date
(`🛫 YYYY-MM-DD`). Other checkbox lines are checklist items and never
appear in task queries. A done task gets `✅ YYYY-MM-DD`, which stands in
for its due date in queries.

```markdown
- [ ] Order tiles 📅 2026-09-28
- [x] Call the plumber 📅 ✅ 2026-09-22
```

<!-- generated: statuses -->

Lines fit in 80 columns; emoji count as two. Links are
`[[path/without/extension]]`, relative to the notes root.

## Tags

A tag is `#` followed by letters, digits, `_`, or `-`, anywhere in the
line. Tags match ignoring case.

<!-- generated: tag-aliases -->

Tags the skills use:

- `#next`: a project's next action. An active project with no open
  `#next` gets a warning.
- `#later`: someday/maybe. Left out of task queries unless `--later` is
  given.
- `#wait`: something you're waiting on from someone else. Things you owe
  are ordinary tasks.
- `#review`: a project review. A completed `#review` task records one.
- `#deadline`: a date a project must meet.

## Projects

A project is a note directly in `project/` (`project/Make Bread.md`) or a
folder directly in `project/` whose home note is `Home.md`
(`project/kitchen/Home.md`). Its fields are the `key: value` items of the
first list after the home note's title. There is no frontmatter.

```markdown
# Make Bread

- status: active
- tag: make-bread

- [x] project #review 📅 ✅ 2026-09-03
- [ ] Buy a banneton #next 📅 2026-09-27
```

- `status`: `active`, `paused`, `waiting`, `done`, or `archived`;
  `active` when missing.
- `tag`: the project's tag in tasks and time logs. None when missing.
- `archived`: the date the project was archived, set by `meta-notes
  archive`.

A project's tasks are every task in its note or folder, plus every task
anywhere carrying its tag. `meta-notes projects` lists projects with their
last review and warnings.

## Editing tasks

Never rewrite an existing task line yourself. To change one:

1. Find it with a focused query, for example
   `meta-notes tasks --tag wait --json`. Each task has `file`, `line`, and
   `text`.
2. Edit it with
   `meta-notes task update <file>:<line> --expect <text> <options>`,
   passing `text` exactly as `--expect`. Options: `--status <c>`,
   `--add-tag <tag>`, `--remove-tag <tag>`, `--due <YYYY-MM-DD|undated|none>`,
   `--start <YYYY-MM-DD|none>`. Combine them in one call.
3. If the command fails because the line changed, re-run the query and
   retry with the current `text`, or ask the user. Never guess a line.

Line numbers from one query stay valid across `task update` calls on that
query's lines, so a batch of edits can use one query.

`--status x` adds `✅ <today>` and any other status removes it. Use
`--add-tag later` to defer, `--status -` to cancel.

## Adding lines

New tasks, Follow up items, and summaries are written into the note
directly. Put tags before date markers:

```markdown
- [ ] Call Sam about the quote #next 📅 2026-09-28
```

## Carrying a task forward

To move an unfinished task to another note, write the new copy in the
target note, then mark the old line `>` with
`meta-notes task update <file>:<line> --expect <text> --status '>'`.
Don't change the old line's dates. `task update` never copies a task.

## Ceremony markers

Checklist lines record whether a ceremony was done. They have no dates,
so they aren't tasks. Daily notes carry `- [ ] plan complete` and
`- [ ] shutdown complete`; weekly notes carry `- [ ] review complete` and
`- [ ] plan complete`.

Check a marker with `meta-notes task update <file>:<line> --expect <text>
--status x`, which appends `✅ <today>`, the day the ceremony was done.
Find the line with `grep -n` in the note. `meta-notes ceremony status
[--date YYYY-MM-DD]` reports all four for a day and its week. A missing
note or marker counts as not done; add the marker line if a note lacks it.

## Notes and structure

- `meta-notes note daily|weekly [YYYY-MM-DD]` creates a plan note from its
  template if needed and prints its path.
- Move, rename, or archive notes only with `meta-notes move`, `rename`,
  or `archive`, which update links, and only after the user confirms the
  exact command. Never use `mv` or `git mv`.
- Workdays are Monday to Friday. Weeks start on Monday.
