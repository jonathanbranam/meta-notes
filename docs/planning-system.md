# Planning System Requirements

Status: draft, 2026-09-21

## Problem

Capture works. Review and commitment don't. Projects and tasks go stale, so
neither I nor an agent can plan a day against them. The first hour at the
desk goes to re-deciding priorities, reading the calendar, and building a
time block from scratch.

The fix is a set of rituals, supported by skills and tooling, that keep the
notes current enough to plan against. The file format changes as little as
possible.

## Principles

- **Markdown in PPARA stays the store.** Vim stays the primary authoring
  tool. Everything else is a layer over the files.
- **One implementation.** Every operation (move, rename, archive, task
  edits, queries) lives in a Python CLI (stdlib only). The Vim plugin, the
  agent, and the local server all call it.
- **Rituals over structure.** A field or convention exists only if a ritual
  uses it.
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

No new syntax beyond a bare 📆.

| Line | Meaning | In task lists |
|---|---|---|
| `- [ ] text` | Checklist item in a note | No |
| `- [ ] text 📆` | Task, no date yet | Yes, as undated |
| `- [ ] text 📆 YYYY-MM-DD` or `🛫 YYYY-MM-DD` | Dated task | Yes |
| Any of the above plus `#later` | Someday/maybe | Only on request |

- Status characters are unchanged: space (open), `x`/`X` (done), `>`
  (rescheduled), `-` (canceled), and the partial states `.`, `o`, `O`.
- `#later` is excluded from task queries by default and listed in its own
  section when requested. This exists on the work copy of meta-notes and
  needs porting back.
- A bare 📆 makes an undated line a task. Reviews prompt for a date.
- Lines should fit in 80 columns. Emoji render two columns wide in most
  terminals.
- `#next` marks a project's next action. A project with no open `#next` is
  flagged as a warning. `#next` is not exclusive with other tags.

### Task age

The age of an open task is the date its line was last edited, taken from
`git blame` at day granularity (notes are committed daily). A task untouched
for a long time is the signal that it's being put off. No created-date
syntax is needed.

### Commitments (open)

Things I owe someone and things I'm waiting on need to be queryable, and so
do PR reviews. Candidate tags: `#owe`, `#wait`, `#pr`. Whether to mark people
(`@name` or a `#tag`) is undecided; the preference is not to add syntax.

## Project model

Project notes may carry optional frontmatter. For folder projects, the
canonical note is `index.md` (to confirm).

```markdown
---
status: active        # active | paused | waiting | done
outcome: One sentence describing done
deadline: 2026-10-30
tag: feature-store    # the tag used in time logs and tasks
revisit: 2026-10-01   # come back to this
reviewed: 2026-09-21  # stamped by the project review
---
```

**Last touched** is derived, never authored. A project was touched on the
most recent of:

- the last day its tag or a `[[project/...]]` link appears in a daily note's
  Log or Actual column
- the last ✅ date on a task inside it
- the last meaningful change to its files (see below)

File mtime is not used, because link rewrites touch unrelated files.

**Meaningful change** means the most recent commit touching a file,
following renames. The CLI never commits; moves and link rewrites land in
the daily commit and count as changes for now. A filter for diffs that only
change `[[link]]` targets or headers is a possible follow-up.

### Reorganizing

- Projects can be converted to areas when they become an ongoing
  responsibility that spawns new projects. The history moves to
  `area/<name>/`, and new projects live in `project/` and link to the area
  (or nest under it; either layout is one `move`).
- Moves apply to a note, a folder, or a whole hierarchy, always with link
  updates.

### Archive tiers

- `archive` stamps `archived: YYYY-MM-DD` in frontmatter.
- Search and task queries skip items archived more than about 12 months
  ago by default, with a flag to include them.
- The CLI regenerates a `.ignore` file that ripgrep respects, so Vim grep
  follows the same rule.
- Old material stays in the tree so links keep resolving. Nothing moves out
  of the notes root.

## Rituals

Each ritual is an agent skill with a template section and a completion
marker that reminders and the dashboard can check.

### Morning (8:00, about 10 minutes)

Starts from the plan made at the previous shutdown.

1. Open today's note and adjust blocks for anything new: meetings, fires.
2. Surface the 2–3 oldest untouched open tasks (not `#later`). For each:
   do today, date it, `#later` it, or cancel it.
3. Start the first block by 8:15. It should be a concrete task chosen the
   night before, not "plan the day".

### Shutdown (end of day, about 15 minutes)

1. **Collect.** Notes are the only inbox.
   - Starred email: each becomes a task, then unstar.
   - Saved Slack: clear a few each day, newest first. Each becomes a task
     with the thread link, or gets unsaved. The backlog gets a cutoff date,
     with everything older bulk-unsaved.
   - Anything else promised or thought of today.
   - The agent turns pasted messages into task lines in the right note.
2. **PR check.** Reviews requested from me, plus the repos I own. Each open
   PR becomes a task dated tomorrow. The review itself gets a morning block.
3. **Projects touched today.** Write the next step for each.
4. **Time log.** Backfill today from memory. A rough log beats none.
5. **Tomorrow.** Create tomorrow's note with a first-pass time block and a
   short list. On Friday, "tomorrow" is Monday.
6. **Commit.** Mark done with `- [x] shutdown complete`.

### Weekly review (Friday, about 9:00–10:30)

The output is a written summary in the weekly note by 11:00, suitable for
sharing with my manager. The agent drafts it from:

- tasks completed this week (✅ dates)
- the week's time report
- meaningful file changes
- daily notes

Then:

1. Plan versus actual for the week.
2. Commitments in both directions, and all tasks untouched for more than 30
   days.
3. Undated 📆 tasks: date each or `#later` it.
4. Project review on the 2–3 projects next in the queue.
5. Scan `#later` for anything that has become live.

### Week plan (Friday afternoon)

1. Read next week's calendar.
2. **Capacity.** Productive hours are free gaps of 90 minutes or more.
   Shorter gaps are listed separately.
3. Meetings to schedule, and deadlines landing next week.
4. Choose 3–5 priorities and place them roughly on days.
5. Friday's shutdown creates Monday's note with a first-pass time block.

### Project review (anytime, 5–10 minutes)

One project per session. See `skills/project-review/SKILL.md`.

- With no argument, it picks the project with the oldest (or missing)
  `reviewed:` date. Repeated sessions work through the whole backlog.
- It shows the files, open tasks inside and outside the project folder, and
  the last meaningful change. It gives the project state in about ten lines.
- It asks for a disposition: continue, pause, done, convert to area, split,
  or merge.
- It walks stale tasks oldest first, in batches sized to the time available.
- It asks for a next action and new tasks, applies the edits, and stamps
  `reviewed:`. Stopping early saves partial progress.

## Skills

| Skill | When | Output |
|---|---|---|
| project-review | Anytime | One project reconciled, `reviewed:` stamped |
| shutdown | End of day | Inboxes cleared, tasks captured, tomorrow planned, commit |
| morning | 8:00 | Adjusted blocks |
| weekly-review | Friday morning | Weekly summary |
| week-plan | Friday afternoon | Next week's note, Monday's note |

Skills ship in `skills/` in this repo and are installed into the agent's
skill directory by symlink. They call the CLI for all reads and edits, using
focused queries (tags, date ranges, folders) to keep agent context small.

## CLI

Specified across several openspec changes, in this order:

- `cli-core`: the CLI itself, with `move`, `rename`, `archive`, and `tasks`
  ported from today's code without behavior changes (no git commits; the
  CLI only reads git), and JSON output on every command
- `find-tasks-enhancements`: the task model (📆 or 🛫 required, bare 📆
  undated), `#later`, tag and date-range filters, a last-edited date, and
  an untouched-days filter
- `task-update`: change status, tags, or date on a specific line, with a
  guard against stale line numbers
- `project-brief`: everything the project review needs in one call
- `cli-init`: `meta-notes init`, including skill install

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
   date ranges, trimmed output), the task model, and task age.
3. Task update, then project brief.
4. Project review skill, then work through the backlog one project at a
   time.
5. Shutdown skill.
6. Weekly review and week plan skills.
7. Morning skill.
8. Dashboard with time logging and reminders.
9. Archive tiers.

## Open questions

- Commitment tags, and whether to mark people.
- Canonical note name for folder projects (`index.md`?).
- Whether the calendar options 2 and 3 are acceptable under work policy.
- A filter for link-only and header-only diffs in last-change dates.
- The age threshold for "untouched" in the morning surface (proposed: 30
  days).
