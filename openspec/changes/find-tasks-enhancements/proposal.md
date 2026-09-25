## Why

Task queries can't tell a live task from a someday item or a plain
checklist, can't filter or group by tag, and can't say how long a task has
sat untouched. The ceremonies in `docs/planning-system.md` (daily planning,
project review, weekly review) depend on all of these.

The work notes repo still keeps its own `tasks.py`, which predates the
plugin and does some of this. `docs/Port tasks and time_log features into
meta-notes.md` lists what it does that the plugin doesn't. Porting those
features lets that repo delete its copy, so there is one implementation. The
time log half of that document is in `time-report-enhancements`.

## Dependencies

- **`cli-core`** (archived 2026-09-25) adds `meta-notes tasks` and the
  `task-query` capability that this change modifies. Nothing blocks.
- **`task-update`** should land after this change, because it writes the
  bare 📆 and `#later` defined here.

The port notes describe the work copy, so the old dependency on "the work
copy's `find_tasks.py` or a written description" is met.

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
- **`#later`.** A `#later` task is never "ready" (see the next item). It
  shows only in its own "Tasks for later" section, and only once its due or
  start date is on or before the reference date. Undated `#later` tasks never
  appear there. Default report and flags: open question 3.
- **Ready by date.** A task is ready on a reference date (default today) when
  it is open, is not `#later`, and has a due date or start date on or before
  that date. Ready tasks are listed grouped by file, with each line printed
  exactly as written (bullet, checkbox, and indentation kept). Local form:
  `tasks.py --by-due-date [YYYY-MM-DD]`. Whether this replaces the week-based
  default report: open question 1.
- **Group by tag.** A new report mode lists ready tasks under `### <tag>`
  headings, sorted alphabetically ignoring case, with `### Not tagged` last.
  Within each tag, tasks are grouped by file. A task with several tags appears
  under each of them. An optional comma-separated list limits the report to
  those tags (local form: `--by-tag admin,cd`).
- **Task age.** `meta-notes tasks` reports `last_edited` per task, the author
  date of the task's line from `git blame`. Uncommitted lines report today.
  Blame runs once per file with matching tasks.
- **`--untouched-days N`** returns only open tasks last edited more than N
  days ago.
- The same parsing applies to `scripts/find_tasks.py`, so daily-note
  templates get the new task model and `#later` exclusion. Task age is
  CLI-only, to keep template rendering fast.
- The `task-query` requirement "Standalone script still works" (same output
  as before) is relaxed: `find_tasks.py` keeps its options, but its output
  follows the new task model.

### Out of scope

- Deleting the work repo's `tasks.py` and `notes.py`. That happens in the
  notes repo once this change ships.

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities
- `task-query`: due-date emojis, task definition (due emoji or 🛫 required,
  bare due emoji undated), `tags`, `#later`, the ready-by-date and
  group-by-tag reports and the tag filter, `last_edited`, `--untouched-days`,
  and the relaxed standalone-output requirement.

## Open Questions

**Please resolve these before design and specs are written.**

1. **Ready report vs. week-based sections. (Under discussion.)** The default
   report sorts every open task into "Past & Current Week" (the due date, or
   the start date if there is no due date, falls on or before this Sunday),
   "Future (>1 Week)", and "No Date". The ready report lists only tasks whose
   due date *or* start date is on or before one reference date. They differ
   in three ways:
   - **Cutoff:** end of this week vs. a single day (today by default).
   - **Start dates:** the week sections ignore 🛫 when there is a due date, so
     a task started today but due in three weeks lands in "Future". The ready
     report counts it as ready.
   - **Coverage:** the week sections show every open task. The ready report
     hides future and undated tasks.

   The daily template's "Due Today" and "Overdue" use `--due-on` and
   `--due-by`, which only look at due dates, so started tasks are missing
   there too. Proposed: use one model. Make "ready as of DATE" the default
   report (today by default, this Sunday for weekly planning), followed by
   "Upcoming", "Undated", and "#later" sections, and drop the week buckets.
2. **Plain checkboxes.** The work copy's ready and by-tag reports only ever
   show dated tasks. Does it report plain `- [ ]` items anywhere, or does the
   proposed task model match it?
3. **`#later` in the default report and filters.** The work copy prints the
   "Tasks for later" section in its default report. Should `meta-notes tasks`
   do the same, or show `#later` only behind a flag? Should `--due-on`,
   `--due-by`, `--folder`, and similar filters exclude `#later`? Should
   `--untouched-days` count it? (Proposed: exclude from filters and
   `--untouched-days` unless the flag is given.)
4. **Flag names.** Keep the work copy's `--by-due-date [DATE]` and
   `--by-tag [TAGS]`, or use names that fit the existing options, such as
   `--ready [DATE]`, `--group-by tag`, and `--tag TAG` (repeatable, and also
   usable as a filter on the other modes)?
5. **Tag matching.** Exact `#tag` only, or also apply the time log aliases
   in `scripts/time_tracking.py` (`#mtg` → `#meeting`, `#pers`/`#per` →
   `#personal`)? Should tasks and time logs share one tag parser?
6. **`last_edited` outside git.** When the notes root isn't a git repo:
   null, or the file's mtime?

## Impact

- `scripts/tasks.py`: due-date emojis, task definition, bare due marker,
  `tags`
- `scripts/find_tasks.py`: `#later`, ready-by-date and group-by-tag reports,
  tag filter, and possibly a new default report (question 1)
- `scripts/meta_notes/query.py`, `scripts/meta_notes/cli.py`: new options,
  `tags` and `last_edited` in JSON, `--untouched-days`
- Tests: `test/unit/test_tasks.py`, `test_find_tasks.py`, `test_query.py`,
  `test_cli.py`
- Daily notes rendered from templates: plain checklists and `#later` items
  drop out of task sections, and the template may switch to the ready report
  (question 1). Golden fixtures in `test/fixtures/templates/` change with it.
- `doc/meta-notes.txt`: task model, due emojis, tags, `#later`, new report
  modes
- `skills/project-review/SKILL.md`: can use `meta-notes tasks` for task age
  and tag queries instead of raw `git blame` and grep
