## Why

Task queries can't tell a live task from a someday item or a plain
checklist, can't filter or group by tag, and can't answer the questions
planning actually asks: what is due today, what is overdue, what is ready to
work on by a given day, and what is scheduled in a given period. The
ceremonies in `docs/planning-system.md` (daily planning, project review,
weekly review) depend on all of these.

The work notes repo still keeps its own `tasks.py`, which predates the
plugin and does some of this. `docs/Port tasks and time_log features into
meta-notes.md` lists what it does that the plugin doesn't. Porting those
features lets that repo delete its copy, so there is one implementation. The
time log half of that document is in `time-report-enhancements`. Task age
(`last_edited`, `--untouched-days`) is in `task-age`.

## Dependencies

- **`cli-core`** (archived 2026-09-25) adds `meta-notes tasks` and the
  `task-query` capability that this change modifies. Nothing blocks.
- **`time-report-enhancements`**, **`task-age`**, and **`task-update`**
  should land after this change. The first reuses the `--date` syntax and
  shared tag parser defined here, `task-age` filters the selection defined
  here, and `task-update` writes the bare 📆 and `#later` defined here.

## What Changes

### Task model

- **Due-date emojis.** 📅, 📆, and 🗓 are all due dates. The work copy uses
  📅, which the plugin currently ignores, so none of its due dates are seen
  today. The plugin writes 📆 (templates, `task-update`).
- **Tasks need a date marker.** A checklist line is a task only when it
  carries a due-date emoji (with or without a date) or `🛫 YYYY-MM-DD`.
  Plain `- [ ]` items are checklist items and are ignored. Any due-date emoji
  used bare marks an undated task. **BREAKING** for task lists in daily
  notes, which currently show every checkbox.
- **Completion date.** A completed task's ✅ date, when present, is used in
  place of its due date for date selection. Most completed tasks have no ✅
  date and keep the due date as the completion date, so they need nothing.
- **Tags.** `Task` gains `tags`: every `#tag` on the line, anywhere in the
  line, stored without the `#`. JSON output includes `tags`.
- **One tag parser.** Tasks and time logs share one tag parser in a new
  `scripts/tags.py`: the pattern `#([\w_-]+)` and the aliases now in
  `scripts/time_tracking.py` (`#mtg` → `#meeting`, `#pers` and `#per` →
  `#personal`). A task tagged `#mtg` is stored with the tag `meeting`, and
  `--tag mtg` and `--tag meeting` match the same tasks. Tag groups
  (`TAG_GROUPS`) stay in time tracking.

### Selecting tasks

- **`--date` takes a day or a period.** Default: today. Accepted forms:
  - `YYYY-MM-DD`: one day
  - `YYYY-MM-DD..YYYY-MM-DD`: an inclusive range
  - `YYYY-MM`: a month
  - `YYYY-Qn`: a quarter
  - `YYYY`: a year

  No other forms. A single day D is the period D..D. The parser is shared
  in a new `scripts/period.py`, and every command that takes a date or range
  uses it (`meta-notes time` in `time-report-enhancements`; `ceremony
  status`, `changes`, and completed-task queries in `planning-skills`).
  Below, the period runs from START to END.
- **Selection modes.** Tasks are still filtered by `--status` (default
  `incomplete`).
  - `--scheduled`: due date **or** start date within START..END. This
    answers "what do I have scheduled in this period?" Tasks dated before
    START, including overdue ones, are left out, and so is a task that
    spans the period with no date inside it. Example: `--scheduled --date
    2026-11` in September lists only November's tasks.
  - `--due`: due date within START..END. Start dates are ignored. With a
    single day, this is "due today". With `--status completed`, it lists
    tasks completed in the period.
  - `--overdue`: due date before START. Start dates are ignored.
  - `--ready`: due date or start date on or before END. This includes
    overdue tasks. Monday planning uses `--ready --date <Sunday>`.
  - `--future`: has a due or start date, but neither is on or before END
    (the complement of `--ready` among dated tasks).
  - `--undated`: a bare due emoji and no start date.
  - `--all`: `--ready`, `--future`, and `--undated` together, which is every
    task of the selected status.
  - With no mode, the report is `--ready` as of today.
  - Modes combine. The text report prints one section per selected mode, in
    the order overdue, due, scheduled, ready, future, undated. Modes overlap
    (a due task is also scheduled and ready), so each task is printed once,
    in the first section that matches. JSON gives each task the `section` it
    was printed in.
- **`#later`.** Every mode leaves out tasks tagged `#later`, including
  `--all` and `--folder`. `--later` includes them, under the same date rules,
  mixed into the same sections as other tasks. For example, `--all --later`
  returns every open task.
- **`--tag TAG`** (repeatable) limits results to tasks with any of the given
  tags.
- **`--group-by tag`** prints the selected tasks under `### <tag>` headings,
  sorted alphabetically ignoring case, with `### Not tagged` last. Within
  each tag, tasks are grouped by file. A task with several tags appears under
  each of them. Local form: `tasks.py --by-tag admin,cd`.
- **Output lines.** Tasks are listed grouped by file, with each line printed
  exactly as written (bullet, checkbox, and indentation kept).

### Removed

- **`--due-on`, `--due-by`, and `--due-between`.** **BREAKING.** They become
  `--due --date D`, `--overdue --date D+1`, and `--due --date START..END`.
- **Week buckets.** The "Past & Current Week", "Future (>1 Week)", and
  "No Date" sections go away. `--ready`, `--future`, and `--undated` cover
  them, so the script needs no week concept. JSON `category` values
  (`past_or_current`, `future`, `no_date`) become the `section` values
  above. **BREAKING** for JSON consumers of the default report.

### Templates and compatibility

- The shipped daily template's "Due Today" and "Overdue" sections switch to
  `--due` and `--overdue`.
- Templates already copied into notes roots by `init` still call the removed
  flags. Updating them is up to each user. Until then, those blocks render as
  the existing failed-command comment (`<!-- Command failed: ... Error: ...
  -->`, showing the usage error) and the CLI reports a warning, so the note
  is still created.
- `scripts/find_tasks.py` and `meta-notes tasks` keep the same options and
  output. The `task-query` requirement "Standalone script still works" (same
  options and output as before) is replaced by one requiring the two to
  match each other.

### Out of scope

- Task age (`last_edited`, `--untouched-days`): the `task-age` change.
- Deleting the work repo's `tasks.py` and `notes.py`. That happens in the
  notes repo once this change ships.

## Capabilities

### New Capabilities
- `date-period`: the shared `--date` syntax (day, `START..END` range, month,
  quarter, year), its validation and error messages, and how it resolves to
  START and END.

### Modified Capabilities
- `task-query`: due-date emojis, the task definition (due emoji or 🛫
  required, bare due emoji undated, plain checkboxes ignored), the ✅ date
  rule, `tags` with shared aliases, `--date` periods and the selection modes
  (`--scheduled`, `--due`, `--overdue`, `--ready`, `--future`, `--undated`,
  `--all`) replacing the week buckets and the `--due-*` options, `#later`
  and `--later`, `--tag` and `--group-by tag`, and the replaced
  standalone-script requirement.
- `template`: the shipped daily template's task sections use `--due` and
  `--overdue`, and the command-block example uses the new options.

## Impact

- New `scripts/tags.py`: shared tag pattern and aliases.
  `scripts/time_tracking.py` imports its aliases from there.
- New `scripts/period.py`: `--date` parsing.
- `scripts/tasks.py`: due-date emojis, task definition, bare due marker, ✅
  date rule, `tags`
- `scripts/find_tasks.py`: selection modes replacing the week buckets and
  `--due-*`, `#later` and `--later`, `--tag`, `--group-by tag`
- `scripts/meta_notes/query.py`, `scripts/meta_notes/cli.py`: new options,
  `tags` and `section` in JSON
- Tests: `test/unit/test_tasks.py`, `test_find_tasks.py`, `test_query.py`,
  `test_cli.py`, `test_time_tracking.py`, and new `test_tags.py` and
  `test_period.py`
- `templates/daily.md`: "Due Today" and "Overdue" switch to `--due` and
  `--overdue`. Golden fixtures in `test/fixtures/templates/` and
  `test/fixtures/init_templates/` change with it. Rendered daily notes also
  lose plain checklist items and `#later` tasks.
- `doc/meta-notes.txt` (`:help meta-notes-cli`) and `requirements.md`: task
  model, due emojis, tags, `--date` periods, selection modes, `#later` and
  `--later`, removed options
