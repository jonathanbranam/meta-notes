## Why

The ceremonies in `docs/planning-system.md` (daily shutdown, daily planning,
weekly review, weekly planning) only work if they're easy to start and quick
to finish. Today there's a single draft skill (`project-review`), and the
agent can't do several things these ceremonies need. It can't total a week of
time logs, list tasks completed in a date range, tell which projects have
gone quiet, or tell whether a ceremony has been done. This change ships a skill
for each ceremony and adds the scripts they depend on.

## Dependencies

- **`note-create`**: `meta-notes note daily|weekly`, which `daily-plan` and
  `weekly-plan` use to create their target notes.
- **`cli-init`**: templates become markdown files shipped with the plugin,
  and skills get installed into the notes root. The template updates here
  edit those files, and the new skills are installed through that mechanism.
  Skills call `meta-notes` by name and stop with an error if it isn't on
  `PATH`; `init` already warns when it isn't.
- **`find-tasks-enhancements`**: the task model, selection modes (`--ready`,
  `--due`, `--overdue`), `#later`, and tag filters.
- **`time-report-enhancements`**: `meta-notes time --date START..END` for
  time-log totals in the weekly review.
- **`task-update`**: skills edit task lines through `meta-notes task update`,
  not by rewriting lines themselves. That change also switches
  `project-review` step 7 to the command; the revision here builds on that
  version.
- **`project-brief`**: the project list used for weekly-review warnings is
  built from the same per-project data.

The skills are written after the CLI commands they call exist, against
their real output, rather than drafted against today's tools (see
design.md).

## What Changes

### Skills (`skills/<name>/SKILL.md`)

- **`daily-shutdown`**: closes out today's note. Collect (starred email,
  saved Slack, anything promised, pasted in by the user), PR check, a next
  step for each project touched today, a time-log check, and a **Follow up**
  list in today's note for the next workday. Then commit, mark
  `shutdown complete`, and offer `daily-plan` as the next step. Friday's
  shutdown is the same as any other day's. The time-log check runs today's
  time report, finds gaps and large stretches that don't clearly map to a
  project or work item, asks about each, and updates the log from the
  answers.
- **`daily-plan`**: one skill whether run in the evening or the next
  morning. It picks the target day (today if today has no plan, otherwise
  the next workday) and always reads the previous workday's note: its Follow
  up list, unfinished blocks, and shutdown status. For Mondays it also reads
  the weekly plan. It takes meetings from a calendar screenshot, creates
  the target note if needed, and fills the Time Block Plan column. It
  doesn't work through old tasks; that is `task-cleanup`'s job.
  A Follow up item that should be tracked becomes a task in place with
  `task update --due <date>` or `--due undated`.
- **`weekly-review`**: works from the week's completed tasks, time report,
  and daily notes. It covers plan versus actual,
  commitments, project warnings (no recent activity, no `#next`,
  project review overdue), and a `#later` scan (anything live gets
  `#later` removed and, if needed, a date). It drafts a summary for my
  manager with two parts: what I did this week and why it matters, then
  important upcoming dates and deadlines. The summary has no "next week" plan; that belongs to
  weekly planning. It ends with a reminder that weekly planning is next,
  usually Friday afternoon.
- **`weekly-plan`**: reads the review and a calendar screenshot of next
  week. It works out capacity (free gaps of 90 minutes or more, with shorter
  gaps listed separately), meetings to schedule, deadlines, and 3–5
  priorities placed roughly on days. The result goes in next week's note.
- **`task-cleanup`** (new, split out of project review): the only skill
  that works through old tasks. It goes through stale and undated tasks
  across all notes, oldest due date first, in batches sized to the
  time available. Each task is kept, dated, `#later`ed, canceled, or marked
  done. Bulk "cancel all" or "later all" is one `task update` call per line
  from the same query; line numbers from one query stay valid across
  updates, so no batch command is needed.
- **`project-review`** (revised): refocused on dead and dormant projects and
  run monthly. Its stale-task walk is removed in favor of
  `task-cleanup`, and its description no longer triggers on task cleanup.
- Every skill has a stated time budget, supports stopping early, and uses
  focused CLI queries instead of reading whole folders. Shared syntax and
  conventions are defined once, in `meta-notes conventions`, not copied
  into each skill. Every skill runs it first.
- The shared conventions cover task edits: take `file`, `line`, and `text`
  from `meta-notes tasks --json`, pass them to `meta-notes task update
  <file>:<line> --expect <text>`, and re-query when the command reports the
  line changed. Tags go before dates (`... #next 📅 <date>`).
- A task carried forward from one note to another (for example, an
  unfinished task copied into a daily note) is marked `>` on the old line
  with `task update --status '>'`, and the skill writes the new copy
  itself; `task update` never copies a task.
- Ceremony markers are checked with `task update --status x`, which
  appends `✅ <today>` to the marker line. The ✅ date records when the
  ceremony was actually done, so a shutdown done a day late is stamped
  with the later day.

### Scripts and CLI

- **`meta-notes ceremony status [--date DATE]`**: reports which ceremony markers
  are checked for a day and its week (shutdown, plan, weekly review, weekly
  plan). Skills use it to find skipped steps. Reminders and the dashboard
  will use it later. A checked marker counts as done with or without a
  trailing `✅` date, and the date, when present, is reported.
- Every date or range option uses the shared `--date` syntax from
  `find-tasks-enhancements` (`date-period`).
- Provided by other changes: time-log totals across a range are
  `meta-notes time --date START..END` (`time-report-enhancements`), and
  tasks completed in a range are `meta-notes tasks --status completed --due
  --date START..END` (`find-tasks-enhancements`, which uses the ✅ date when
  present and the due date otherwise).
- **`meta-notes conventions`**: prints the shared syntax and conventions
  the skills follow, as markdown. The prose lives in a markdown file in the
  package, and the parts defined in code (status characters, due emoji,
  tag aliases) are generated from `scripts/tasks.py` and `scripts/tags.py`,
  so the text always matches the installed CLI. Any agent can use it, not
  only Claude Code skills.
- **`meta-notes projects`**: one line per project with status, last review,
  and warnings (no open `#next`, no recent activity, review overdue).
  Activity comes from the dates written in the project: the latest
  `YYYY-MM-DD` (up to today) in its files' names and contents and in tasks
  anywhere with its `tag`. None in the last 30 days means no recent
  activity. No git history or file mtimes are read. A project's review is overdue
  when its latest completed `#review` is more than 30 days old, or it has
  none. Project fields and tags follow "Project model" in
  `docs/planning-system.md`.
- **`#waiting` alias**: `scripts/tags.py` normalizes `#waiting` to `#wait`,
  so commitment queries (`--tag wait`) find both.

### Templates

- **`daily.md`**: adds a `## Follow Up` section and a ceremony checklist
  (`- [ ] plan complete`, `- [ ] shutdown complete`).
- **`weekly.md`**: adds `## Review` and `## Plan` sections, and a checklist
  (`- [ ] review complete`, `- [ ] plan complete`).
- Existing notes aren't migrated. Skills and `ceremony status` treat a
  missing section or marker as not done.

## Capabilities

### New Capabilities
- `ceremony-skills`: the six shipped skills, with each skill's inputs,
  outputs, handoffs, time budget, and stop-early behavior
- `ceremony-status`: ceremony markers in notes and how their status is read
- `project-list`: the project overview with warnings
- `conventions`: the shared syntax and conventions printed by `meta-notes
  conventions`, and which parts are generated from code

### Modified Capabilities
- `template`: the daily and weekly templates gain ceremony sections and
  markers
- `task-query`: `#waiting` becomes an alias of `#wait`

## Impact

- `skills/`: five new skills, and `project-review` revised
- `scripts/meta_notes/`: new `ceremony`, `conventions`, and `projects`
  subcommands, and the conventions markdown file
- Plugin template files (from `cli-init`): `daily.md` and `weekly.md` updated
- `test/unit/`: pytest coverage for each new command
- `docs/planning-system.md`, `README.md`: ceremonies and skills documented
