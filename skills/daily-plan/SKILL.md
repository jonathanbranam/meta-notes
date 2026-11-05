---
name: daily-plan
description: Plan one workday (or, in a personal root, one day) in a meta-notes notes root, about 10–15 minutes, in the evening after shutdown or the next morning. Use when the user says "plan my day", "plan tomorrow", "daily plan", or accepts the offer at the end of daily-shutdown. Puts the day's meetings in the Time Block first, reads the weekly plan, warns when the work doesn't fit the open time, fills the Plan column and picks a first block. It does not close out the day (daily-shutdown) or work through old tasks (task-cleanup).
---

# Daily Plan

Plan one day: the right target day, its meetings first, the weekly plan
and due work checked against the open time, and a concrete first block. In the morning the goal is the first block started,
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

3. Read the mode: if the conventions end with a "Personal mode"
   section, this is a personal root. Where a step below differs for it, it
   says so; otherwise the steps are the same.

## Hard rules

- Change existing task and checklist lines only with
  `meta-notes task update`, with `file`, `line`, and `text` from
  `meta-notes tasks --json` (the `line` is optional). Never rewrite them by hand.
- If `task update` says the line changed, re-query and retry, or ask.
- Change the Time Block only with `meta-notes time-block update` (or
  `replace` for several rows). Never edit the table by hand. The
  `time-block` skill has the rules and the user's style for these edits.
- Don't work through old or overdue tasks one by one. Mention the count
  and suggest `task-cleanup` instead.
- Don't read git history or file modification times.
- If the user says stop, go to "Stopping early".

## Steps

Workdays are Monday to Friday. In a personal root every day is a day:
the next day is tomorrow, weekends included, you plan inside the
personal day (07:00 to 21:00), and there is no PR, Slack or email step.

### 1. Pick the target day

Run `meta-notes ceremony status --json`. If `daily-plan` is not done for
today, the target is today; otherwise it is the next workday (tomorrow, in
a personal root). State the
choice in one line ("Planning Friday 2026-09-25."). The user can override
it. Call it TARGET, and the workday before it PREV.

### 2. Meetings into the Time Block

This is the very next action after picking TARGET: before outlook, tasks,
the previous day or any conversation about the work. The user should see
the day's meeting skeleton in the note right away.

1. Run `meta-notes note daily <TARGET>` to get (or create) TARGET's note.
2. Run `meta-notes calendar --date <TARGET> --json`.
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
3. Write every meeting into the Plan column of the `### Time Block` table
   at its times (an event fills every row it spans, with travel as its own
   rows; see `meta-notes conventions`), before planning any other work.
   Write each Plan cell with `meta-notes time-block update <note> --time
   9:30am [--through 10:15am] --plan '<text>'` (add `--create` for a row
   the table lacks), never by editing the table by hand; it pads to the
   column and refuses a filled cell unless `--expect '<old text>'`
   matches. When it reports a cell that's too wide, shorten the text. To
   write several rows at once, use `meta-notes time-block replace` (see
   `meta-notes conventions`).
   - Meeting text (the `mtg:` and `(opt) ` prefixes, and what to do when
     events overlap) follows `meta-notes conventions`.
4. Tell the user the shape of the day in one line: the meetings and the
   open time left (free gaps; count the gaps of 90 minutes or more
   separately, as `weekly-plan` does).

### 3. Read the previous workday and the weekly plan

Run `meta-notes ceremony status --date <PREV> --json`. If `daily-shutdown`
is not done, say so in one line and continue; don't run the shutdown. A
personal root has no daily shutdown, so skip this check there.

If PREV's note exists, read from it:

- its `## Follow Up` list
- its Time Block rows whose Plan cell has work but whose Actual cell is
  empty or different (unfinished blocks)

On every day, not only a Monday, read the `## Plan` section of TARGET's
weekly note (the `weekly-plan` entry's `note` in
`meta-notes ceremony status --date <TARGET> --json`), if it exists. When it
has the per-day breakdown (`### <Weekday> <date>` headings), take TARGET's
slice and every unchecked item from earlier days of that week. These are
what the week's plan expects of TARGET. If the note has no per-day
breakdown (an older week), use the week-level priorities and deadlines as
before and don't restructure the note.

In a personal root there is no shutdown to have kept the breakdown
current, so catch it up here: from PREV's note and Time Block, check off
the breakdown items that got done (`meta-notes task update ... --status
x`) and move unchecked items from PREV forward to TARGET's slice or a
later day, with `meta-notes note write` (`--lines`, `--expect`), after
confirming with the user.

### 4. Gather

- Outlook: run `meta-notes outlook refresh` (today's note and tomorrow's,
  when it exists), and `meta-notes outlook refresh --date <TARGET>` if
  TARGET is later. It changes only the `### Outlook` section. Tell the
  user the forecast in one line from TARGET's note; if a status says
  `failed`, say so and go on.
- Due: `meta-notes tasks --due --date <TARGET> --json`
- Overdue: `meta-notes tasks --overdue --date <TARGET> --json` (count and
  the few that matter today; nothing more)
- Waiting on others: `meta-notes tasks --all --tag wait --json`, the ones
  due on or before TARGET or undated

Reconcile the weekly plan's slice for TARGET (step 3) with the due and
overdue tasks into one list. Say which source an item came from only where
they disagree (planned for today but not due, or due today but not in the
plan), and ask where such an item belongs.

Summarize in a few lines: meetings, the day's work, Follow up items,
waits to chase.

### 5. Fit check

Compare the work assigned to or due on TARGET (the combined list, plus
what the week's plan has coming due later this week) with TARGET's
remaining open time from step 2. Estimate each item roughly; ask when you
can't. If it doesn't fit, say so explicitly, with the numbers, for example
"Open time today is about 2 hours; the items for today add up to about 4.
Which should slip?" Don't proceed as if everything will get done: let the
user pick what slips, and move those items (a later day in the breakdown
with `meta-notes note write`, and a new due date with
`meta-notes task update --due`). Also say so when a deadline later in the
week no longer has room on the days that remain.

### 6. Follow up items

For each Follow up item from PREV, ask what to do:

- **Track it**: make it a task in place with
  `meta-notes task update "<PREV note>:<line>" --expect '<text>'
  --due <YYYY-MM-DD>` (or `--due undated`). Get the line with
  `grep -n` in PREV's note.
- **Do it TARGET**: it goes in the plan (step 7).
- **Drop it**: `--status -`.

To carry an unfinished task into TARGET's note, write the copy there and
mark the old line `>` with `task update ... --status '>'`. Never copy a
`🔁` marker or its rule into the copy: recurring tasks stay in their home
note.

### 7. Write the plan

The meetings are already in the Time Block (step 2).

1. Put the most important work in the largest free blocks of the Plan
   column, written with `meta-notes time-block update` or `replace` as in
   step 2.
2. Name a concrete first block (what, and the first action), and tell
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
