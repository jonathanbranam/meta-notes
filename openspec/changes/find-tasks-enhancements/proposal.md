## Why

Task queries can't tell a live task from a someday item or a plain
checklist, can't filter or group by tag, and can't answer the questions
planning actually asks: what is due today, what is overdue, and what is
ready to work on by a given day. The ceremonies in `docs/planning-system.md`
(daily planning, project review, weekly review) depend on all of these.

The work notes repo still keeps its own `tasks.py`, which predates the
plugin and does some of this. `docs/Port tasks and time_log features into
meta-notes.md` lists what it does that the plugin doesn't. Porting those
features lets that repo delete its copy, so there is one implementation. The
time log half of that document is in `time-report-enhancements`. Task age
(`last_edited`, `--untouched-days`) is in `task-age`.

## Dependencies

- **`cli-core`** (archived 2026-09-25) adds `meta-notes tasks` and the
  `task-query` capability that this change modifies. Nothing blocks.
- **`task-age`** and **`task-update`** should land after this change.
  `task-age` filters the selection defined here, and `task-update` writes
  the bare 📆 and `#later` defined here.

## What Changes

- **Due-date emojis.** 📅, 📆, and 🗓 are all due dates. The work copy uses
  📅, which the plugin currently ignores, so none of its due dates are seen
  today. The plugin writes 📆 (templates, `task-update`).
- **Task model.** A checklist line is a task only when it carries a due-date
  emoji (with or without a date) or `🛫 YYYY-MM-DD`. Plain `- [ ]` items are
  checklist items and are no longer reported. Any due-date emoji used bare
  marks an undated task. **BREAKING** for task lists in daily notes, which
  currently show every checkbox.
- **Tags on tasks.** `Task` gains `tags`: every `#tag` on the line, found with
  `#([\w_-]+)`, anywhere in the line, stored without the `#`. JSON output
  includes `tags`.
- **Reference period.** `--date` takes a single day or a period. Default:
  today. Accepted forms:
  - `YYYY-MM-DD`: one day
  - `YYYY-MM-DD..YYYY-MM-DD`: an inclusive range
  - `YYYY-MM`: a month
  - `YYYY-Qn`: a quarter
  - `YYYY`: a year

  No other forms: no relative names such as `next-month`, and no ISO weeks.

  Periods are mainly for planning from the CLI or a skill ("what do I have
  scheduled in November?"), so the month, quarter, and year forms save
  working out start and end dates by hand. Templates can use them too,
  although template variables are day-level only (`date`, `week_start`,
  `week_end`). A single day D is the period D..D. Below, the period runs
  from START to END.
- **Selection modes.** Only open tasks are selected.
  - `--scheduled`: due date **or** start date within START..END. This
    answers "what do I have scheduled in this period?" Tasks dated before
    START (including overdue ones) are left out. Example: `--scheduled
    --date 2026-11` in September lists only November's tasks.
  - `--due`: due date within START..END. Start dates are ignored. With a
    single day, this is "due today".
  - `--overdue`: due date before START. Start dates are ignored.
  - `--ready`: due date or start date on or before END. This includes
    overdue tasks. Monday planning uses `--ready --date
    {{week_end:%Y-%m-%d}}`.
  - `--future`: has a due or start date, but neither is on or before END
    (the complement of `--ready` among dated tasks).
  - `--undated`: a bare due emoji and no start date.
  - `--all`: `--ready`, `--future`, and `--undated` together, which is every
    open task.
  - With no mode, the report is `--ready` as of today.
  - Modes combine. The text report prints one section per selected mode, in
    the order overdue, due, scheduled, ready, future, undated. Modes overlap
    (a due task is also scheduled and ready), so each task is printed once,
    in the first section that matches. JSON gives each task the `section` it
    was printed in.
- **`--due-on`, `--due-by`, and `--due-between` removed.** **BREAKING.**
  They become `--due --date D`, `--overdue --date D+1`, and
  `--due --date START..END`. The shipped daily template switches to `--due`
  and `--overdue`. Daily templates already copied into notes roots by `init`
  still call the old flags (open question 1).
- **Week buckets removed.** The "Past & Current Week", "Future (>1 Week)",
  and "No Date" sections go away. `--ready` with the week's Sunday,
  `--future`, and `--undated` cover them. Templates already have
  `{{week_end}}`, and weeks can also be passed as ranges, so the script
  needs no week concept. JSON `category`
  values (`past_or_current`, `future`, `no_date`) become the `section` values
  above. **BREAKING** for JSON consumers of the default report.
- **`#later`.** Every mode leaves out tasks tagged `#later`, including
  `--all` and `--folder`. `--later` includes them, under the same date rules
  as the selected modes, mixed into the same sections as other tasks. For
  example, `--all --later` returns every open task. JSON marks them through
  `tags`.
- **Group by tag.** `--group-by tag` prints the selected tasks under
  `### <tag>` headings, sorted alphabetically ignoring case, with
  `### Not tagged` last. Within each tag, tasks are grouped by file. A task
  with several tags appears under each of them. `--tag TAG` (repeatable)
  limits results to tasks with any of the given tags, with or without
  `--group-by`. Local form: `tasks.py --by-tag admin,cd`.
- **Output lines.** Tasks are listed grouped by file, with each line printed
  exactly as written (bullet, checkbox, and indentation kept).
- `scripts/find_tasks.py` and `meta-notes tasks` keep the same options and
  output, so templates and the CLI stay in step.
- The `task-query` requirement "Standalone script still works" (same options
  and output as before) is replaced by one requiring `find_tasks.py` and
  `meta-notes tasks` to match each other.

### Out of scope

- Task age (`last_edited`, `--untouched-days`): the `task-age` change.
- Deleting the work repo's `tasks.py` and `notes.py`. That happens in the
  notes repo once this change ships.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities
- `task-query`: due-date emojis, task definition (due emoji or 🛫 required,
  bare due emoji undated), `tags`, the `--date` reference day or period and
  selection modes (`--scheduled`, `--due`, `--overdue`, `--ready`,
  `--future`, `--undated`, `--all`)
  replacing the week buckets and the `--due-*` options, `#later` and
  `--later`, `--group-by tag` and `--tag`, and the replaced
  standalone-script requirement.

## Open Questions

**Please resolve these before design and specs are written.**

1. **Notes roots with old templates.** `init` copies `templates/daily.md`
   into each notes root and doesn't overwrite it on a re-run, so existing
   roots keep calling `--due-on` and `--due-by`. Once those flags are gone,
   new daily notes in those roots render an error. Options:
   - (a) Drop the flags. Update each root's template by hand or with
     `meta-notes init --force`, which also overwrites any template edits.
   - (b) Keep `--due-on` and `--due-by` as hidden, undocumented aliases for
     one release, printing a deprecation warning to stderr.

   Proposed: (a). There are only a couple of notes roots, and the switch is a
   two-line template edit.
2. **Tasks that span the period.** A task started in October and due in
   December has no date inside November. Should `--scheduled --date 2026-11`
   list it? Proposed: no. `--scheduled` lists only tasks with a date inside
   the period, and `--ready` covers work already under way.
3. **Period flag name.** Keep one `--date` that takes a day or a period, or
   use a separate name for periods (for example `--period 2026-11`, or
   `--from`/`--to`)? Proposed: one `--date`, since a day is just a one-day
   period.
4. **Plain checkboxes.** The work copy's reports only ever show dated tasks.
   Does it report plain `- [ ]` items anywhere, or does the proposed task
   model match it?
5. **Tag matching.** Exact `#tag` only, or also apply the time log aliases
   in `scripts/time_tracking.py` (`#mtg` → `#meeting`, `#pers`/`#per` →
   `#personal`)? Should tasks and time logs share one tag parser?
6. **Shared period syntax.** `planning-skills` proposes
   `meta-notes tasks --completed-between <start> <end>` and
   `meta-notes time-report --from <date> --to <date>`, and
   `time-report-enhancements` proposes `meta-notes time --date <day>`.
   Proposed: one `--date` period grammar for all of them. A `--completed`
   mode here selects tasks whose ✅ date is in the period (replacing
   `--completed-between`), and `meta-notes time --date <period>` covers the
   range report. `planning-skills` and `time-report-enhancements` would be
   updated to match.

## Impact

- `scripts/tasks.py`: due-date emojis, task definition, bare due marker,
  `tags`
- `scripts/find_tasks.py`: `--date` period parsing, selection modes
  replacing the week buckets and `--due-*`, `#later` and `--later`, `--group-by tag`, `--tag`
- `scripts/meta_notes/query.py`, `scripts/meta_notes/cli.py`: new options,
  `tags` and `section` in JSON
- Tests: `test/unit/test_tasks.py`, `test_find_tasks.py`, `test_query.py`,
  `test_cli.py`
- `templates/daily.md`: "Due Today" and "Overdue" switch to `--due` and
  `--overdue`. The weekly template can add `--ready --date {{week_end}}`.
  Golden fixtures in `test/fixtures/templates/` and
  `test/fixtures/init_templates/` change with them. Rendered daily notes also
  lose plain checklist items and `#later` tasks.
- `doc/meta-notes.txt` (`:help meta-notes-cli`) and `requirements.md`: task
  model, due emojis, tags, `--date` periods, selection modes, `#later` and
  `--later`, removed `--due-*` options
