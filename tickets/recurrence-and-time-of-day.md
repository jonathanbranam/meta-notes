---
id: mn-ba09
title: Recurrence and time of day for tasks and reminders
status: proposal, awaiting the human's review
---

# Recurrence and time of day for tasks and reminders

A design proposal. Nothing here is built, no spec is edited, and the version
is not bumped. It comes from the life-assistant ticket (bridle `phyy`): the
human says meta-notes "has most of what we need" but lacks recurrence, and
also lacks an exact time of day. They use the Obsidian Tasks plugin and like
its syntax.

## Summary of the recommendation

1. **Recurrence** uses Obsidian Tasks syntax as is: `🔁 every 3 months` on a
   task line, with an optional trailing `when done`. The human's ~130
   maintenance lines then move over unchanged.
2. **Completing a recurring task** (`task update --status x`) marks the line
   done, stamps `✅`, and inserts the next occurrence as a new open line
   directly below it, in the same edit. The CLI reports both lines.
3. **Time of day** is a separate `⏰ HH:MM` marker (24-hour, local time) that
   goes with the due date. It is a proposal choice, not a settled one; the
   alternative is `📅 2026-10-01 15:00` (see [Time of day](#time-of-day)).
4. **Reminder** is not a new kind of thing: a task with a due date and a
   `⏰` time. Who tells the human when one is due (phyy Q4) stays outside
   meta-notes; the CLI only answers "what is due by now".
5. **v1 rules** are the ones in the human's notes (`every N days|weeks|months`,
   with or without `when done`) plus years and `every weekday`. Weekday and
   month-day rules come in a second step.

## What exists today

Checked in `scripts/tasks.py`, `scripts/meta_notes/task_update.py`,
`scripts/meta_notes/query.py` and the specs `task-query`, `task-update`,
`date-period`, `cli`.

- A **task** is a checkbox line with a due emoji (`📅`, `📆` or `🗓`, with or
  without a date) or a valid `🛫 YYYY-MM-DD`. A bare due emoji means undated.
  Other checkbox lines are checklist items and are not queried.
- Dates are day-precision `YYYY-MM-DD`. There is no time anywhere.
  `tasks.py` finds them by regex; `_DUE_DATE_PATTERN` ignores anything after
  the date, so extra text there does not break today's parser.
- **`task update <file>:<line> --expect <text>`** edits one line in place as
  marker tokens (`_DUE_MARKER`, `_START_MARKER`, `_COMPLETED_MARKER`), never
  re-rendering from a parsed `Task`. Options: `--status`, `--add-tag`,
  `--remove-tag`, `--due`, `--start`, `--no-completed`. It writes only the
  target line, and the `--expect` guard protects against stale line numbers.
- **Completion** (`r-43d5`): `--status x` appends `✅ <today>` unless the line
  already has one, the due date is today, or `--no-completed`. Any other
  status removes `✅`.
- **Queries** (`r-4720`, `r-ebb9`): modes select by due and start date; a
  completed task's `✅` date stands in for its due date.
- There is **no `task done`** command (the ticket text mentions one). Done is
  `task update --status x`. There is also **no `task add`**: the CLI can edit
  a checkbox line but not create one. See [Adjacent gap](#adjacent-gap-creating-tasks).
- Nothing in the CLI ever inserts a line; `task update` only rewrites the
  target. Recurrence breaks that invariant, which is the biggest change here.

## Syntax

Follow the Obsidian Tasks plugin, so lines work in both tools.

```
- [ ] replace whole house water filter 🔁 every 3 months 📅 2026-07-01
- [ ] Buy 4 bags of salt 🔁 every month when done 📅 2025-07-24
- [ ] check attic for mice 🔁 every 2 weeks when done 📅 2024-12-09
- [ ] call the plumber ⏰ 15:00 📅 2026-10-01
- [ ] take vitamins ⏰ 08:00 🔁 every day 📅 2026-10-01
```

- **Marker**: `🔁` (optionally followed by the emoji variation selector, like
  the other markers), then the rule text. The rule runs to the next date
  emoji marker (`📅 📆 🗓 🛫 ✅ ⏰`), to the first `#tag`, or to the end of
  the line. Tags stay before the dates as `task-update` places them today.
- **Rule** (case-insensitive, single spaces):

  ```
  every [N] (day|week|month|year)[s] [when done]
  ```

  `N` defaults to 1. `every day`, `every 2 weeks`, `every month when done`.
- **Later steps**, same grammar family as Obsidian: `every weekday`,
  `every Monday[, Wednesday]`, `every N weeks on Monday`,
  `every month on the 1st|last`. Obsidian also has `every other X` and
  `every January`; list them as out of scope until the human asks.
- **`when done`**: the next date counts from the completion date instead of
  the due date.
- **Only `📅`, `✅` and `🔁`** appear in the human's notes. `⏳` (scheduled)
  is not a meta-notes marker and stays unsupported; `🛫` start is supported
  as described below.
- A `🔁` without a due or start date, or with a rule the parser does not
  recognize, is **not recurring**. The line is still a task if it has a due
  emoji; queries report a warning for the bad rule rather than failing.
  A bare `📅` with `when done` is valid: the base is the completion date.
- **Reference date** for the next occurrence, in Obsidian's order: without
  `when done`, the due date, else the start date; with `when done`, the
  completion date. If a non-`when done` line has neither date, no next
  occurrence is made and the command warns.

## Parsing

In `scripts/tasks.py`:

- `Task` gains `recurrence: str | None` (the rule text as written, so it can
  be echoed back) and, once time of day lands, `due_time` and `start_time`
  (see below). It keeps parsing lazily by regex like the dates do.
- A small pure module (proposed `scripts/recurrence.py`, tested in
  `test/unit/test_recurrence.py`, stdlib only per `languages.md`) holds
  `parse_rule(text) -> Rule | None` and `next_date(rule, base) -> date`.
  Month and year steps clamp to the last day of the month (Jan 31 plus one
  month is Feb 28), as Obsidian does. Keeping it separate lets `task_update`,
  `query` and later `brief` and `ceremony` share it without importing each
  other.
- `is_task` is unchanged: a `🔁` line that has no due emoji and no `🛫` date
  is a checklist item, as today.
- `task_update.py` gets `_RECURRENCE_MARKER` alongside the other marker
  patterns and adds `🔁` to `_DATE_EMOJI_PATTERN`, so `--add-tag` still puts
  tags before the first marker.

## What completing an occurrence does

`meta-notes task update <file>:<line> --expect ... --status x` on a line that
has a valid `🔁` rule:

1. Marks the line `[x]` and stamps `✅ <today>`. **Recurring lines always get
   `✅`**, even when due today, an exception to `r-43d5`; the done line is the
   record of when it was done, and `when done` needs it.
2. Computes the next occurrence from the reference date (above).
3. Inserts a **new open line directly below** the done line: the same text
   and indentation and `🔁` rule, `[ ]` status, no `✅`, with the due date
   replaced by the next date and the start date, if any, moved by the same
   number of days as the due date. The time (`⏰`) is copied unchanged. This
   matches Obsidian's default of the next occurrence below.
4. Writes both lines in one file write. Nothing else in the file changes.

The done line keeps its own line number, so the guard and a caller's
bookkeeping still work. The new line is at `line + 1` and every later line in
the file shifts by one; callers must re-read the file. The result reports it
(see CLI surface).

Edge cases:

- **Already done, set to done again**: no new occurrence (the same rule as
  `r-43d5` keeping the completion date). This is what keeps a repeated call
  from spawning twice.
- **Canceled `-`, rescheduled `>`, reopened, partial**: no occurrence. Only
  the transition to done spawns one. Reopening a done recurring line does
  **not** delete the line that was spawned; the human or agent removes it.
  Say so in the docs.
- **`--no-completed`** on a recurring line: rejected with a usage error, since
  the next date may depend on `✅`. (Alternative: honor it and use today
  as the completion date.)
- **`--due` in the same call** as `--status x`: the reference date is the
  due date after the edit, as `r-43d5` already treats it.
- **`--no-recur`** option, new: complete the line without spawning the next
  occurrence (for a series that is finished). Simpler than deleting the line
  after the fact. Only the recurring rule stays on the done line.
- **Completed late**: with plain `every 3 months` and due 2026-07-01 done on
  2026-10-05, the next date is 2026-10-01, already overdue. Obsidian behaves
  this way for the plain form and `when done` exists for the case where the
  gap should count from completion. Recommendation: keep that behavior, so it
  is predictable and matches the human's tool; see open question 2.
- **The done line keeps `🔁`** (as Obsidian does), so the history reads
  "every 3 months, done on X".
- **Recurring task in a daily-note copy** (`>` carry-forward): unaffected.
  `>` never spawns. A recurring line that is completed inside a daily note
  spawns its next occurrence in that same note, which is wrong for a series
  that lives in `area/`. Recommendation: recurring tasks belong in one home
  note, and the planning skills copy without `🔁`; see open question 5.

## Time of day

Two syntaxes were considered. Both bind the time to the due date and are
24-hour `HH:MM` in the local time zone (the `[calendar] timezone` setting
applies to calendar display only, and this feature does not use it).

| | A: `📅 2026-10-01 15:00` | B: `⏰ 15:00` |
|---|---|---|
| Reads as | one "due at" token | a separate marker |
| Existing parsers | `_DUE_DATE_PATTERN` ignores the time; `_set_marker_date` keeps it when the date changes | new marker, new pattern, like `🛫` |
| Obsidian Tasks | its trailing-marker parse stops at `15:00`, so the `📅` is no longer read | if `⏰ 15:00` sits before the Obsidian markers, it is just description text; every other marker still parses |
| Task query | one marker, one place to look | two markers to keep in step |
| Bare time | impossible, a time needs a date | possible to write, needs a rule |

**Recommendation: B, `⏰ HH:MM`**, placed just before the first date marker
(the same place `--add-tag` uses; tags before it stay first), so
`- [ ] call plumber ⏰ 15:00 📅 2026-10-01 ✅ ...`. It keeps Obsidian
reading the rest of the line while the human still uses both tools, and it
leaves the strict `📅 YYYY-MM-DD` shape that every current parser and the
specs assume. If the human stops using Obsidian, A is a smaller change to
the line and worth revisiting.

Rules:

- The time belongs to the due date. `⏰` with no valid due date is ignored
  and the query warns. A start time (`🛫 ... ⏰`) is not supported.
- `HH:MM`, 00:00 to 23:59. Anything else is invalid: the line still parses
  as a task without a time and warns. No `3pm`, no seconds, no time ranges,
  no end time, no time zones.
- **Recurrence** copies the time unchanged to the next occurrence.
- **Overdue and due semantics**: a task with no time is due for the whole
  day, as today. A timed task is due at that moment. `--overdue` and `--due`
  keep comparing days unless `--at` is given (below), so nothing in the
  existing report changes for existing lines.
- **Reminder**: a task with a `⏰` time and a due date, and no more. Whether
  reminders need a separate tag or template, and how the human is told,
  are life-assistant concerns.

## CLI surface

`meta-notes tasks` and its `--json` (spec `task-query` `r-8297`):

- Each task in `--json` gains `time` (`"15:00"` or null), `recurrence` (the
  rule text or null) and `recurs_from_completion` (bool, true for
  `when done`). Existing fields keep their names and meaning.
- New option **`--at TIME|now`**: evaluates the selection at a time of day
  as well as a date. With `--at`, a task due `START` with a `⏰` time earlier
  than `--at` is `--overdue`, one due at or before it is `--due`/`--ready`,
  and later ones fall to `--future`. Tasks without a time are unchanged. This
  is what the life assistant would run to find "what is due now". `--at`
  needs a single day in `--date`, and its value is `now` or `HH:MM`.
- **Sorting** stays file order in text output. Agents sort by `due` then
  `time` from the JSON.
- The default query and the text output are unchanged. A completed task's
  `✅` still stands in for its due date, so a completed recurring line is
  listed once, in the period it was done.
- A dedicated view of recurring tasks is not needed in v1: `--json` carries
  `recurrence`, and the agent filters. (A `--recurring` filter is a small
  addition if wanted.)

`meta-notes task update`:

- `--status x` on a recurring line does the completion above. No new option
  is needed for the normal case.
- **`--no-recur`** (new) completes without spawning.
- **`--recur <rule>|none`** (new), like `--due`: sets or removes the `🔁`
  rule. The rule is validated with the same parser and rejected with a usage
  error when invalid; `none` removes the marker and its rule text. A new
  marker goes just before the first date marker.
- **`--time HH:MM|none`** (new): sets or removes `⏰`.
- `--json` result gains `created`: the new line's text, its line number and
  its file, or null when nothing was spawned. Existing `old` and `new` fields
  keep describing the target line. Warnings (invalid rule, missing base
  date) go in `warnings`, as the "no longer a task" warning does now.
- The command still edits one file and never stages or commits (`cli` spec).

## Adjacent gap: creating tasks

The life assistant must create tasks and reminders from messages, and the CLI
has no way to add a checkbox line to a note. That is outside this proposal's
scope (recurrence and time of day), but it will block capture. The suggested
step is a `meta-notes task add <file> <text> [--due ... --time ... --recur ...]`
that appends a task line. Flagged here as open question 6; not part of the
build breakdown unless the human wants it.

## Interaction with existing specs

Each of these spec changes would be made by the build tasks, on their own
branches, not here.

| Spec | Change |
|---|---|
| `task-update` `r-43d5` Completion date | Exception: a recurring line always gets `✅` |
| `task-update` (new requirements) | Spawning the next occurrence; `--no-recur`; `--recur`; `--time`; `created` in JSON; the "update writes only the target line" statements become "only the target line and its spawned line" |
| `task-update` `r-c0ba` | A recurring completion is the one edit that adds a line |
| `task-query` `r-21a1` A task needs a date marker | Unchanged; state that `🔁` and `⏰` are not date markers |
| `task-query` `r-8297` JSON | New fields `time`, `recurrence`, `recurs_from_completion` |
| `task-query` `r-4720` Selection modes | `--at`; the mode table unchanged when `--at` is absent |
| `task-query` `r-ebb9` | Unchanged |
| `cli` | Nothing structural; `task update` and `tasks` gain options |
| `date-period` | Unchanged; `--at` does not use the period grammar |
| `project-brief`, `ceremony-skills`, `conventions`, `agent-prime` | The conventions text lists the markers; add `🔁` and `⏰`. Skills that copy tasks forward should copy without `🔁` (question 5) |

Also to update in the build: `doc/meta-notes.txt`, `README.md`,
`scripts/meta_notes/conventions.md` and `prime.md` (product text, per
`product-skills.md`), the `task-cleanup` and daily skills if they write task
lines, and the version (MINOR).

The vim plugin: `autoload/meta_notes/` has no task parsing of its own that
this affects, per the specs; the build should confirm with a grep before
starting. `after/syntax/markdown.vim` could highlight `🔁` and `⏰` as an
optional last step.

## Open questions for the human

1. **Time of day syntax**: `⏰ 15:00` (recommended, Obsidian-safe) or
   `📅 2026-10-01 15:00`? Do you still open these notes in Obsidian?
2. **Completed late**: with `every 3 months 📅 2026-07-01` done on
   2026-10-05, should the next occurrence be 2026-10-01 (Obsidian's
   behavior, already overdue) or the first date on the schedule after today
   (2027-01-01)? Recommend the first, matching your current tool. (I have not
   checked how your Obsidian version handles this; your vault will tell.)
3. **Always stamp `✅` on recurring lines**, even when done on the due date?
   Recommended: yes, so the history is complete.
4. **Where does the next occurrence go**: below the done line (Obsidian's
   default, recommended) or above? Do you want the done occurrences kept in
   `Home Maintenance.md` as your file does now, or moved to the archive?
5. **Recurring tasks in daily and weekly notes**: should completion of a
   `🔁` line copied into a daily note spawn there? Recommended: recurring
   lives in one home note (`area/`), and the skills never copy `🔁` forward.
6. **Task creation**: add `meta-notes task add` (needed for capture) as part
   of this work, or as its own task?
7. **Reminder semantics**: is a task with `⏰` enough, or should reminders
   also have a lead time ("remind me 1 day before")? Recommended: no lead
   time in v1; use a second dated task.
8. **v1 rules**: are `every N days|weeks|months|years [when done]` and
   `every weekday` enough to start? Which of `on Monday`, `on the 1st`,
   `every other week` do you need first?
9. **Untimed tasks and `--at`**: an untimed task due today is treated as
   due all day. Is that what you want for "what is due now", or should
   untimed tasks appear from a morning cutoff?
10. **Time zone**: local time of the machine running the CLI (the NUC) is
    proposed. Does the time zone ever differ from the machine's?

## Suggested build breakdown

Each is its own task, in this order; each brings its spec, tests, docs and
a MINOR version bump. 1 and 2 are independent of 3, and 4 needs 1 and 3 in
its options list only.

1. **Recurrence rules** (`scripts/recurrence.py`, unit tests): grammar for
   v1, `next_date`, month-end clamping, `when done`. No CLI yet.
2. **Parse and report**: `Task.recurrence`, `tasks --json` fields, the
   warning for a bad rule, `conventions.md` and `prime.md` marker text.
3. **Time of day**: `⏰` parsing in `tasks.py` and `task_update.py`
   (`--time`), `time` in `--json`, the warning for a time without a date,
   syntax highlight if wanted.
4. **Complete and spawn**: `--status x` inserts the next line; `created` in
   the result; `--no-recur`; `--recur`; the `r-43d5` exception; the vader
   and pytest tests for the whole matrix above (done twice, cancel, late,
   `when done`, indentation, CRLF files, last line without newline).
5. **`--at` query**: selection with a time of day, `now`.
6. **Weekday and month-day rules**: `every weekday`, `every Monday`,
   `every N weeks on Monday`, `every month on the 1st|last`.
7. **(If wanted) `task add`**: create a task line with due, time and rule.
8. **Migration check**: run `meta-notes tasks --json` over a copy of the
   human's `Home Maintenance.md` to confirm the ~130 lines parse and every
   rule is recognized. A read-only check, done on a copy; do not edit the
   notes repo.

Steps 1 and 4 carry the risk (date arithmetic and the first line-inserting
edit); the rest are small.
