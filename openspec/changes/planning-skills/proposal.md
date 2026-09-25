## Why

The ceremonies in `docs/planning-system.md` (daily shutdown, daily planning,
weekly review, weekly planning) only work if they're easy to start and quick
to finish. Today there's a single draft skill (`project-review`), and the
agent can't do several things these ceremonies need. It can't total a week of
time logs, list tasks completed in a date range, summarize the week's file
changes, or tell whether a ceremony has been done. This change ships a skill
for each ceremony and adds the scripts they depend on.

## Dependencies

- **`note-create`**: `meta-notes note daily|weekly`, which `daily-plan` and
  `weekly-plan` use to create their target notes.
- **`cli-init`**: templates become markdown files shipped with the plugin,
  and skills get installed into the notes root. The template updates here
  edit those files, and the new skills are installed through that mechanism.
- **`find-tasks-enhancements`**: the task model, selection modes (`--ready`,
  `--due`, `--overdue`), `#later`, and tag filters.
- **`time-report-enhancements`**: `meta-notes time --date START..END` for
  time-log totals in the weekly review.
- **`task-age`**: `last_edited` and `--untouched-days`. Task cleanup and
  daily planning both rank tasks by age.
- **`task-update`**: skills edit task lines through `meta-notes task update`,
  not by rewriting lines themselves.
- **`project-brief`**: the project list used for weekly-review warnings is
  built from the same per-project data.

Skills can be drafted before these land, written against today's tools the
way `project-review` is. Each draft notes which steps to switch over when
the CLI support lands.

## What Changes

### Skills (`skills/<name>/SKILL.md`)

- **`daily-shutdown`**: closes out today's note. Collect (starred email,
  saved Slack, anything promised, pasted in by the user), PR check, a next
  step for each project touched today, time-log backfill, and a **Follow up**
  list in today's note for the next workday. Then commit, mark
  `shutdown complete`, and offer `daily-plan` as the next step. Friday's
  shutdown is the same as any other day's.
- **`daily-plan`**: one skill whether run in the evening or the next
  morning. It picks the target day (today if today has no plan, otherwise
  the next workday) and always reads the previous workday's note: its Follow
  up list, unfinished blocks, and shutdown status. For Mondays it also reads
  the weekly plan. It takes meetings from a calendar screenshot, surfaces the
  2–3 oldest untouched tasks, creates the target note if needed, and fills
  the Time Block Plan column.
- **`weekly-review`**: drafts a summary suitable for my manager from the
  week's completed tasks, time report, meaningful file changes, and daily
  notes. It covers plan versus actual, commitments, project warnings
  (untouched, no `#next`, project review overdue), and a `#later` scan. It
  ends with a reminder that weekly planning is next, usually Friday
  afternoon.
- **`weekly-plan`**: reads the review and a calendar screenshot of next
  week. It works out capacity (free gaps of 90 minutes or more, with shorter
  gaps listed separately), meetings to schedule, deadlines, and 3–5
  priorities placed roughly on days. The result goes in next week's note.
- **`task-cleanup`** (new, split out of project review): works through stale
  and undated tasks across all notes, oldest first, in batches sized to the
  time available.
- **`project-review`** (revised): refocused on dead and dormant projects and
  run monthly or quarterly. Its stale-task walk is removed in favor of
  `task-cleanup`, and its description no longer triggers on task cleanup.
- Every skill has a stated time budget, supports stopping early, and uses
  focused CLI queries instead of reading whole folders. Shared syntax and
  conventions are defined once, not copied into each skill.

### Scripts and CLI

- **`meta-notes ceremony status [--date DATE]`**: reports which ceremony markers
  are checked for a day and its week (shutdown, plan, weekly review, weekly
  plan). Skills use it to find skipped steps. Reminders and the dashboard
  will use it later.
- **`meta-notes changes --date START..END`**: summarizes notes changed in a
  period from git history (committed and uncommitted), per file, with
  rename-only changes marked so they can be ignored.
- Every date or range option uses the shared `--date` syntax from
  `find-tasks-enhancements` (`date-period`).
- Provided by other changes: time-log totals across a range are
  `meta-notes time --date START..END` (`time-report-enhancements`), and
  tasks completed in a range are `meta-notes tasks --status completed --due
  --date START..END` (`find-tasks-enhancements`, which uses the ✅ date when
  present and the due date otherwise).
- **`meta-notes projects`**: one line per project with status, `reviewed:`,
  last touched, and warnings (no open `#next`, untouched, review overdue).

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
- `change-summary`: meaningful file changes in a period
- `project-list`: the project overview with warnings

### Modified Capabilities
- `template`: the daily and weekly templates gain ceremony sections and
  markers

## Open Questions

- Where the shared conventions file lives, given that `cli-init` installs
  every directory in `skills/` as a skill (for example, a reserved
  `skills/_shared/` that `init` skips).
- Do skills assume `meta-notes` is on `PATH`, or does `init` record the
  plugin path somewhere the skills can read?
- The shape of the weekly summary for my manager: fixed sections (Done / In
  progress / Blocked / Next week), or prose.
- The threshold for "project review overdue" (proposed: 30 days since the
  oldest `reviewed:`).

## Impact

- `skills/`: five new skills, and `project-review` revised
- `scripts/meta_notes/`: new `ceremony`, `changes`, and `projects`
  subcommands
- Plugin template files (from `cli-init`): `daily.md` and `weekly.md` updated
- `test/unit/`: pytest coverage for each new command
- `docs/planning-system.md`, `README.md`: ceremonies and skills documented
