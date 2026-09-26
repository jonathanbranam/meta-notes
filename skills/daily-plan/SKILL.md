---
name: daily-plan
description: Plan one workday in a meta-notes notes root, about 10–15 minutes, in the evening after shutdown or the next morning. Use when the user says "plan my day", "plan tomorrow", "daily plan", or accepts the offer at the end of daily-shutdown. Fills the Time Block Plan column and picks a first block. It does not close out the day (daily-shutdown) or work through old tasks (task-cleanup).
---

# Daily Plan

Plan one day: the right target day, its meetings and due work, and a
concrete first block. In the morning the goal is the first block started,
not a polished plan.

## Time budget

About 10–15 minutes. Say so in one line when you start.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.

## Hard rules

- Change existing task and checklist lines only with
  `meta-notes task update`, with `file`, `line`, and `text` from
  `meta-notes tasks --json` or `grep -n`. Never rewrite them by hand.
- If `task update` says the line changed, re-query and retry, or ask.
- Don't work through old or overdue tasks one by one. Mention the count
  and suggest `task-cleanup` instead.
- Don't read git history or file modification times.
- If the user says stop, go to "Stopping early".

## Steps

Workdays are Monday to Friday.

### 1. Pick the target day

Run `meta-notes ceremony status --json`. If `daily-plan` is not done for
today, the target is today; otherwise it is the next workday. State the
choice in one line ("Planning Friday 2026-09-25."). The user can override
it. Call it TARGET, and the workday before it PREV.

### 2. Read the previous workday

Run `meta-notes ceremony status --date <PREV> --json`. If `daily-shutdown`
is not done, say so in one line and continue; don't run the shutdown.

If PREV's note exists, read from it:

- its `## Follow Up` list
- its Time Block rows whose Plan cell has work but whose Actual cell is
  empty or different (unfinished blocks)

When TARGET is a Monday, also read the `## Plan` section of TARGET's
weekly note (the `weekly-plan` entry's `note` in
`meta-notes ceremony status --date <TARGET> --json`), if it exists.

### 3. Gather

- Meetings: run `meta-notes calendar --date <TARGET> --json`.
  - `ok` true: use its `days[0].events` as TARGET's meetings. Tell the
    user in one line how old the export is (`source.age_days`) and pass
    on each of its `warnings` (a stale or missing export, `email` not
    set). Don't ask for a screenshot.
  - `ok` false because calendar support isn't installed: tell the user
    to run `meta-notes init` in the notes root (the error names the exact
    command), and offer to continue from a screenshot of TARGET's
    calendar.
  - `ok` false otherwise (for example, no export): tell the user they can
    export from Google Calendar (Settings, Import & export, Export) and
    save the `.zip` into the `ics/` folder the error names, then you'll
    re-run the command, or provide a screenshot of TARGET's calendar.
    Continue with whichever they provide.
- Due: `meta-notes tasks --due --date <TARGET> --json`
- Overdue: `meta-notes tasks --overdue --date <TARGET> --json` (count and
  the few that matter today; nothing more)
- Waiting on others: `meta-notes tasks --all --tag wait --json`, the ones
  due on or before TARGET or undated

Summarize in a few lines: meetings, due work, Follow up items, waits to
chase.

### 4. Follow up items

For each Follow up item from PREV, ask what to do:

- **Track it**: make it a task in place with
  `meta-notes task update "<PREV note>:<line>" --expect '<text>'
  --due <YYYY-MM-DD>` (or `--due undated`). Get the line with
  `grep -n` in PREV's note.
- **Do it TARGET**: it goes in the plan (step 5).
- **Drop it**: `--status -`.

To carry an unfinished task into TARGET's note, write the copy there and
mark the old line `>` with `task update ... --status '>'`.

### 5. Write the plan

1. Run `meta-notes note daily <TARGET>` to get (or create) TARGET's note.
2. Fill the Plan column of the `### Time Block` table: meetings at their
   times, then the most important work in the largest free blocks. Edit
   only the Plan cells, keeping the table's column widths.
3. Name a concrete first block (what, and the first action), and tell
   the user.

### 6. Mark

Find `plan complete` with `grep -n` in TARGET's note (add
`- [ ] plan complete` under the Week Plan link if missing) and check it
with `meta-notes task update ... --status x`.

## Stopping early

When the user says stop: save the plan cells and task updates made so
far, say what's left, and end without further questions. Leave
`plan complete` unchecked unless the Plan column and first block are
written.
