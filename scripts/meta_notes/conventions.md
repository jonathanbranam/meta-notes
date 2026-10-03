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
for its due date in queries. A time of day goes with the due date:
`⏰ 15:00` before the dates, or `📅 2026-10-01 15:00`. It is for humans and
reminders; a task is due today by its date, whatever its time.

A recurring task has `🔁 every 3 months` (or `every day`, `every 2 weeks`,
`every year`, `every weekday`, any of them with `when done` after) before
the dates. `meta-notes tasks --json` reports it as `recurrence` and
`recurs_from_completion`; a `🔁` rule it doesn't support is a warning. A
recurring task lives in one home note (usually in `area/`). **Never copy a
`🔁` line forward** into a daily or weekly note, or into another note:
write the task without the `🔁` marker and leave the original where it is.
Completing one with `task update --status x` stamps `✅` and adds the next
occurrence as a new open line **above** the done line (the `created` field
of `--json`), so the lines after it move down one: re-query before the next
edit. `--no-recur` completes without the next one; `--recur <rule>|none`
sets or removes the rule.

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

## Tasks with notes and subtasks

A task is its checkbox line plus its **notes**: the indented lines under it
that aren't checkboxes, up to the next line indented no deeper. A
**subtask** is a checkbox line indented under another, to any depth, with
notes of its own (a deeper note belongs to the nearest checkbox above it
with a smaller indent). Notes may come after the subtasks. A blank line
ends the task. Dates aren't inherited: each line keeps its own, so a dated
subtask can sit under an undated parent. `meta-notes tasks --json` gives
each task's `notes`, `parent` and `subtasks`. To read one task as a whole,
use `meta-notes task show <file>:<line>` (the line and its notes) or
`--tree` (every subtask too), and don't parse the indentation yourself.

To write them, use these, each with `--expect` (what you read; `task show`
prints it) and one write, and never edit the lines yourself:
`meta-notes task notes <file>:<line> --expect <notes> --text <notes>`
replaces a task's notes (indented lines as written; empty removes them);
`meta-notes task add <file> <text> --under <line> --expect <parent line>`
adds a subtask after its notes and subtasks; `meta-notes task replace
<file>:<line> --expect <lines> --text <lines> [--tree]` replaces a task and
its notes, or its whole subtree. Pass long text with `-` to read it from
standard input. Marking a subtask done through `task update` sets its
ancestors' status for you (` .oO` by thirds of the subtasks done, `x`
only when all are); don't set the parent's status yourself. Line
numbers move after a write above them, so re-read before the next one.

## Editing tasks

Never rewrite an existing task line yourself. To change one:

1. Find it with a focused query, for example
   `meta-notes tasks --tag wait --json`. Each task has `file`, `line`, and
   `text`.
2. Edit it with
   `meta-notes task update <file>:<line> --expect <text> <options>`,
   passing `text` exactly as `--expect`. Options: `--status <c>`,
   `--text <words>` (replaces the task's words, keeping its dates; tags
   among the old words go too), `--add-tag <tag>`, `--remove-tag <tag>`,
   `--due <YYYY-MM-DD|undated|none>`,
   `--start <YYYY-MM-DD|none>`, `--time <HH:MM|none>`,
   `--recur <rule|none>`, `--no-recur`. Combine them in one call.
3. If the command fails because the line changed, re-run the query and
   retry with the current `text`, or ask the user. Never guess a line.

Line numbers from one query stay valid across `task update` calls on that
query's lines, so a batch of edits can use one query. The exception is
completing a recurring task, which adds a line above it.

`--status x` (or `X`) adds `✅ <today>` unless the line already has
`✅`, its due date is today, or `--no-completed` is given; the CLI always
writes lowercase `x` unless the task is already done, in which case it
preserves the existing case to avoid unnecessary diffs.
Recurring lines always get `✅ <today>`. Any other status
removes `✅`. Use `--add-tag later` to defer, `--status -`
to cancel.

## Editing the Time Block

A tilde before a time means approximately: `home ~9:20`, `until ~10:55`.
For a row that already happened and didn't go as planned, wrap the Plan
in single tildes (`~feed the dogs~`), never double. Don't rewrite the Plan;
give Actual a short summary of what happened instead. A past row with
an empty Plan gets the Plan `no plan` (the day had no plan for that block)
and a short Actual summary.

Never edit the daily note's `### Time Block` table yourself. Write its
Plan and Actual cells with
`meta-notes time-block update <file> --time 9:30am [--through 10:15am]
--plan <text>` (or `--actual <text>`, or both). It finds rows by time and
pads each cell to its column. A filled cell is only overwritten with
`--expect <its current text>`; when it reports a mismatch, re-read the
cell and retry, or ask the user. `--create` adds a row the table lacks.
When it says the text is too wide, shorten it. To rewrite several rows
at once (reorder, move, add a row), use
`meta-notes time-block replace <file> --time 9:00am --through 10:00am
--expect <rows> --text <rows>`: each is the rows as `| time | plan |
actual |` lines (padding optional), `--expect` is what you read and is
compared cell by cell, and nothing is written unless every check passes.
Every row of the range must stay in `--text`. `update` is for one cell or
a range set to the same text. Check-ins may use
`meta-notes checkin actual` instead.

## Editing the Time Log

A tilde before a time means approximately: `~9:00` for the start or end.

Never edit the entries under the daily note's `### Log` yourself; the user
usually has the note open in Vim. An entry is a `- ` header line plus its
indented lines (`* start:`, `* end:`, notes).

- `meta-notes time-log append <file> --prev '- Work' --prev-start 09:45
  --prev-open --close-prev --text '- Packed #trip' --start 13:00
  [--end 14:00] [--note <text>]...` adds an entry at the end. The `--prev`
  options must match the last entry, or nothing is written; `--close-prev`
  ends that entry at `--start`. `--first` is for an empty log.
- `meta-notes time-log update <file> --expect <entries> --text <entries>`
  replaces whole entries, found by their exact text, with zero or more
  entries: edit, split, merge or delete (empty `--text`). On a mismatch
  it shows the likely entries; re-read and retry, or ask the user.

A gap or overlap is reported as a warning and still written; fixing times
may take several calls.

## Adding lines

Add a task with `meta-notes task add <file> <text> [--due <date>]
[--time HH:MM] [--recur <rule>] [--start <date>] [--tag <tag>]`; it
validates the date, time and rule and appends the line (`--line <n>`
inserts before line n). Follow up items and summaries are written into
the note directly. Put tags before date markers:

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
