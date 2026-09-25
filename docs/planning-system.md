# Planning System Requirements

Status: draft, 2026-09-21

## Problem

Capture works. Review and commitment don't. Projects and tasks go stale, so
neither I nor an agent can plan a day against them. The first hour at the
desk goes to re-deciding priorities, reading the calendar, and building a
time block from scratch.

The fix is a set of ceremonies, supported by skills and tooling, that keep the
notes current enough to plan against. The file format changes as little as
possible.

## Principles

- **Markdown in PPARA stays the store.** Vim stays the primary authoring
  tool. Everything else is a layer over the files.
- **One implementation.** Every operation (move, rename, archive, task
  edits, queries) lives in a Python CLI (stdlib only). The Vim plugin, the
  agent, and the local server all call it.
- **Ceremonies over structure.** A field or convention exists only if a
  ceremony uses it.
- **Warn, don't enforce.** Missing next actions, stale projects, and skipped
  reviews are surfaced, never blocking.
- **Small units of review.** Any review can be done in 5–10 minutes between
  meetings and resumed later.
- **Work and personal are separate roots.** Same code, separate notes
  directories, no cross-root reads. Work data never leaves the work machine.

## Constraints

### Work

- No external services and no Google API access, including for the agent.
- AI use happens inside interactive agent sessions (Claude Code). A single
  `claude -p` is acceptable; scripted or scheduled agent automation is not.
- Calendar details may be shared with the agent manually (e.g. screenshot).
- macOS only. Local server on 127.0.0.1 is fine.

### Personal

- Integrations and an AI harness are allowed but not required.

## Task model

No new syntax beyond a bare 📅.

| Line | Meaning | In task lists |
|---|---|---|
| `- [ ] text` | Checklist item in a note | No |
| `- [ ] text 📅` | Task, no date yet | Yes, as undated |
| `- [ ] text 📅 YYYY-MM-DD` or `🛫 YYYY-MM-DD` | Dated task | Yes |
| Any of the above plus `#later` | Someday/maybe | Only on request |

- Status characters are unchanged: space (open), `x`/`X` (done), `>`
  (rescheduled), `-` (canceled), and the partial states `.`, `o`, `O`.
- `#later` is excluded from task queries by default and listed in its own
  section when requested. This exists on the work copy of meta-notes and
  needs porting back.
- A bare 📅 makes an undated line a task. Reviews prompt for a date.
- Lines should fit in 80 columns. Emoji render two columns wide in most
  terminals.
- `#next` marks a project's next action. A project with no open `#next` is
  flagged as a warning. `#next` is not exclusive with other tags.

### Task age

Age comes from dates already written in the notes, not from git history
or file mtimes. A stale task has an old due date or sits in a note whose
dates are all old; abandoned tasks and projects are months or years stale,
so this is enough. A `git blame` last-edited date (`task-age`) is deferred.
No created-date syntax is needed.

### Commitments

Things I'm waiting on are tasks tagged `#wait`. `#waiting` is accepted as an
alias and normalized to `#wait`. Things I owe someone are ordinary tasks,
with no tag of their own. `#pr` is not a commitment tag; it already means
something else. Whether to mark people (`@name` or a `#tag`) is undecided;
the preference is not to add syntax.

## Project model

A project is either a single note (`project/make-bread.md`) or a folder
whose home note is `Home.md` (`project/make-bread/Home.md`). Project data
is plain markdown, parsed the way tasks are. There is no frontmatter.

```markdown
# Make Bread

- status: active
- tag: make-bread

- [x] project #review 📅 ✅ 2026-09-03
- [ ] Buy a banneton #next 📅 2026-09-27
- [ ] Bake for the party #deadline 📅 2026-10-30
```

**Fields.** They are `key: value` items in the first list after the home
note's title:

- `status`: `active`, `paused`, `waiting`, `done`, or `archived`; `active`
  when missing.
- `tag`: the tag used in time logs and tasks for this project. A project
  without one has no associated tag.
- `archived`: the date the project was archived, added with
  `status: archived` when it moves to `archive/project/`.

**Tagged tasks** carry everything else, anywhere in the project:

- `#review`: the tag names the work to do, a project review. A completed
  `#review` task records one, and the latest ✅ date among them is the last
  review; a project with none has never been reviewed. The bare 📅 makes
  the line a task, so `meta-notes tasks --status completed --tag review`
  finds it. Reviews are usually suggested, not scheduled: a project is due
  for one when it has no recent activity or hasn't been reviewed in a
  long time. A `#review` task with a
  due date schedules one when that's wanted, which is the uncommon case,
  for example the date to reconsider a paused project.
- `#deadline`: a date the project must meet.
- `#next`: the project's next action (see Task model).

**Project tasks** are the signal of work on a project: every task in the
project's note or folder, plus every task anywhere carrying the project's
`tag`, both open and completed. Completed tasks and their ✅ dates show
recent progress; open tasks and their dates (see Task age) show what's
waiting. A project's **latest date** is the latest `YYYY-MM-DD` up to today
in its file names, its markdown headings (`## Notes 2026-09-25`), and its
project tasks other than `#review` tasks; an active project has recent
meeting notes and updates. Skills read this list and assess the project from it. There is no
separate "last touched" date.

### Reorganizing

- Projects can be converted to areas when they become an ongoing
  responsibility that spawns new projects. The history moves to
  `area/<name>/`, and new projects live in `project/` and link to the area
  (or nest under it; either layout is one `move`).
- Moves apply to a note, a folder, or a whole hierarchy, always with link
  updates.

### Archive tiers

- Archiving always moves the item into `archive/`. An archived project
  also gets `status: archived` and an `archived: YYYY-MM-DD` field in its
  home note. For other items, the archive date is the date of the commit
  that moved them.
- Search and task queries skip items archived more than about 12 months
  ago by default, with a flag to include them.
- The CLI regenerates a `.ignore` file that ripgrep respects, so Vim grep
  follows the same rule.
- Old material stays in the tree so links keep resolving. Nothing moves out
  of the notes root.

## Ceremonies

Each ceremony is an agent skill with a template section and a completion
marker that reminders and the dashboard can check. A ceremony that has a
natural successor ends by offering it, never by running it.

| Ceremony | Skill | When | Offers next |
|---|---|---|---|
| Daily shutdown | daily-shutdown | End of each workday | daily-plan |
| Daily planning | daily-plan | After shutdown, or next morning | — |
| Weekly review | weekly-review | Friday morning, by 11:00 | weekly-plan (reminder) |
| Weekly planning | weekly-plan | Friday afternoon | — |
| Task cleanup | task-cleanup | Anytime, 5–10 minutes | — |
| Project review | project-review | Monthly | — |

### Daily shutdown (end of day, about 15 minutes)

Closes out today's note. It does not plan tomorrow.

1. **Collect.** Notes are the only inbox.
   - Starred email: each becomes a task, then unstar.
   - Saved Slack: clear a few each day, newest first. Each becomes a task
     with the thread link, or gets unsaved. The backlog gets a cutoff date,
     with everything older bulk-unsaved.
   - Anything else promised or thought of today.
   - The agent turns pasted messages into task lines in the right note.
2. **PR check.** Reviews requested from me, plus the repos I own. Each open
   PR becomes a task dated for the next workday.
3. **Projects touched today.** Write the next step for each.
4. **Time log.** Run today's time report and look for gaps and for large
   stretches that don't clearly map to a project or work item. Ask about
   each, then update the log from the answers. A rough log beats none.
5. **Follow up.** Write a short list in today's note of what to pick up on
   the next workday: unfinished work, promised replies, the first thing to
   do. This survives even if planning is skipped.
6. **Commit** and mark `- [x] shutdown complete`.
7. **Offer daily planning** for the next workday. Declining is normal on a
   busy day; planning then happens the next morning.

Friday's shutdown is the same as any other day's.

### Daily planning (about 10–15 minutes)

One skill whether run in the evening after shutdown or the next morning.

1. **Pick the target day.** If today's note has no plan, plan today.
   Otherwise plan the next workday. State the choice in one line.
2. **Read the previous workday's note**, always: its Follow up list, its
   unfinished blocks, and whether shutdown was completed. When the target
   day is a Monday, also read the weekly plan.
3. **Gather:** meetings (calendar screenshot), due and overdue tasks, PR
   tasks, and open commitments due soon.
4. **Write the plan:** create the target day's note if needed, fill the
   Time Block Plan column, and pick a concrete first block.
5. Mark `- [x] plan complete`. In the morning, the goal is the first block
   started by 8:15, not a polished plan.

### Weekly review (Friday, about 9:00–10:30)

The output is a written summary in the weekly note by 11:00, suitable for
sharing with my manager. It covers Monday through Friday; weekend work,
which is rare, isn't reviewed. The agent drafts it from:

- tasks completed this week (✅ dates)
- the week's time report
- daily notes and their Follow up lists

Then:

1. Plan versus actual for the week.
2. Commitments in both directions.
3. Warnings only: projects with no recent activity or no open
   `#next`, and a reminder to run project review when any project's last
   `#review` is more than 30 days old or missing.
4. Scan `#later` for anything that has become live.
5. Mark the review complete and remind me that weekly planning is next,
   usually scheduled for Friday afternoon.

### Weekly planning (Friday afternoon)

1. Read the weekly review and next week's calendar.
2. **Capacity.** Productive hours are free gaps of 90 minutes or more.
   Shorter gaps are listed separately.
3. Meetings to schedule, and deadlines landing next week.
4. Choose 3–5 priorities and place them roughly on days.
5. Write the plan into next week's note. Monday's daily planning reads it.

### Task cleanup (anytime, 5–10 minutes)

Works down the backlog of stale tasks across all notes, independent of
projects. This is the only ceremony that works through old tasks; daily
planning and project review leave it to this skill.

- Lists overdue tasks oldest due date first, plus undated 📅 tasks,
  in batches sized to the time available.
- For each: keep, date it, `#later`, cancel, or done. Bulk "cancel all" or
  "later all" for very old batches.
- Stopping early is fine; the next run picks up the oldest again.

### Project review (monthly, 5–10 minutes per project)

Cleans up dead and dormant projects. One project per session. See
`skills/project-review/SKILL.md`.

- With no argument, it picks the project with the oldest (or missing)
  `#review`. The first pass works through the whole backlog; after that it
  runs monthly.
- It shows the files and the project tasks, open and completed. It gives
  the project state in about ten lines.
- It asks for a disposition: continue, pause, done, convert to area, split,
  or merge.
- It asks for a next action, applies the edits, and adds
  `- [x] project #review 📅 ✅ <today>` to the home note.
  Stopping early saves partial progress. Task-by-task cleanup is left to
  task cleanup.

## Skills

Skills ship in `skills/` in this repo and are installed into the notes
root's `.claude/skills/` by `meta-notes init`. They call the CLI for all
reads and edits, using focused queries (tags, date ranges, folders) to keep
agent context small. See the `planning-skills` change.

## CLI

Specified across several openspec changes, in this order:

- `cli-core`: the CLI itself, with `move`, `rename`, `archive`, and `tasks`
  ported from today's code without behavior changes (no git commits; the
  CLI only reads git), and JSON output on every command
- `find-tasks-enhancements`: the task model (📅 or 🛫 required, bare 📅
  undated), `#later`, and tag and date-range filters. A last-edited date
  and untouched-days filter (`task-age`) are deferred.
- `task-update`: change status, tags, or date on a specific line, with a
  guard against stale line numbers
- `project-brief`: everything the project review needs in one call
- `archive-project-status`: `archive` sets `status: archived` and
  `archived:` on a project's home note
- `cli-init`: `meta-notes init`, including skill install
- `note-create`: `meta-notes note`, creating daily, weekly, and other notes
  from templates, with template rendering moved to Python
- `planning-skills`: the ceremony skills and the queries they need

The Vim plugin becomes a thin caller. Read-only task buffers gain mappings
that edit the source line through `task update`.

## Calendar

Options in order of setup effort:

1. **Screenshot to the agent.** Allowed today and used first.
2. **AppleScript through Calendar.app**, which already syncs the Google
   subscription locally. Slow at querying events, so it must be limited to
   one calendar and one week.
3. **A small Swift EventKit script.** Same local data, fast, and needs one
   macOS permission prompt.

Options 2 and 3 need a policy check first. Reading is lower risk than
creating events, which would sync back to Google.

## Local dashboard

- A stdlib `http.server` bound to 127.0.0.1, one instance per notes root.
- Change detection by polling mtimes every 1–2 seconds, pushed to the
  browser with Server-Sent Events. kqueue is avoided because it needs a
  descriptor per file and Vim's write strategy can replace inodes.
- **Views:** today's blocks, commitments, deadlines, stale projects,
  untouched tasks, and this week's capacity.
- **Writes, all through the CLI:** quick time-log entry (start and stop on a
  tag) and task status changes.
- **Reminders:** browser notifications work from localhost but only while
  the tab is open. A launchd job running `osascript` notifications covers
  the rest by checking completion markers (for example, no shutdown marker by
  17:30, or no weekly summary by Friday 10:45). Reminders never block.

## Email and Slack reset

- **Email:** one-time bulk archive of everything older than two weeks except
  starred mail. Shutdown keeps starred at zero after that.
- **Slack saved items:** drained daily as part of shutdown, with a cutoff for
  bulk removal.

## Sequence

1. CLI core: move, rename, archive, and tasks, ported unchanged.
2. find_tasks enhancements: the work-side changes (`#later`, tag filters,
   date ranges, trimmed output) and the task model.
3. Task update, then project brief.
4. Project review skill, then work through the backlog one project at a
   time.
5. Note creation in the CLI (`note-create`).
6. Planning skills (`planning-skills`): daily shutdown, daily planning,
   weekly review, weekly planning, and task cleanup, with the supporting
   scripts.
7. Dashboard with time logging and reminders.
8. Archive tiers.

## Open questions

- Whether to mark people in commitments.
- Whether the calendar options 2 and 3 are acceptable under work policy.
- The threshold for "no recent activity" on a project (proposed: 30 days
  since its latest date).
