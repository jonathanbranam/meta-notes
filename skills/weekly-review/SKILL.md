---
name: weekly-review
description: Friday weekly review of the Monday–Friday workweek in a meta-notes notes root, about 60–90 minutes, done by 11:00. Use when the user says "weekly review", "review my week", or "write my weekly summary". Drafts a summary for the user's manager in the weekly note's Review section and flags stale projects and commitments. It does not plan next week (that is weekly-plan).
---

# Weekly Review

Look back at the workweek, surface what needs attention, and write a
summary suitable for sending to the user's manager.

## Time budget

About 60–90 minutes, finished by 11:00 on Friday. Say so in one line when
you start. Each step below can stand alone if the user has less time.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.

## Hard rules

- The period is Monday to Friday of the current week (MON..FRI). Weekend
  work isn't reviewed.
- Change existing task lines only with `meta-notes task update`, with
  `file`, `line`, and `text` from `meta-notes tasks --json`. If it says
  the line changed, re-query and retry, or ask. Never rewrite by hand.
- The summary has no plan for next week. That is `weekly-plan`.
- Read git history only through `meta-notes changes`; don't run `git` or
  read file modification times.
- If the user says stop, go to "Stopping early".

## Steps

### 1. Gather (quietly)

For a review on Friday 2026-09-25, MON..FRI is 2026-09-21..2026-09-25.

- Completed: `meta-notes tasks --status completed --due --date MON..FRI
  --json`
- Time: `meta-notes time --date MON..FRI --json` (totals, per tag, per
  day)
- Ceremonies and note paths: `meta-notes ceremony status --date <day>
  --json` for each day MON to FRI. Read each existing daily note's
  `## Follow Up` list and `## Notes` headings, not whole folders.
- The week's plan: the `## Plan` section of this week's weekly note (the
  `weekly-plan` entry's `note`), if any.
- Changed notes: `meta-notes changes --date MON..FRI --json`. Skip
  entries with `rename_only` true and notes under `plan/daily/` and
  `plan/week/` (read above). The rest are prompts for work the other
  inputs missed. If the command fails, say so in one line and continue
  without it.

### 2. Plan versus actual

In a few lines: the week's planned priorities and what happened to each,
the biggest unplanned time sinks (from per-tag time), and skipped
shutdowns or plans. Ask the user to correct anything.

Then, in one batch, list the changed notes the other inputs don't already
account for and ask which were real work worth a line in the summary.
Don't match them against tasks or time entries; judge from what you've
read, and ask when unsure.

### 3. Commitments

- Waiting on others: `meta-notes tasks --all --tag wait --json`. For each
  that's overdue or stale, ask: chase, re-date (`--due`), or done.
- Owed by the user: ask once, "Anything you owe someone that isn't a
  task?" Write new ones as tasks in the right note.

### 4. Project warnings

Run `meta-notes projects --warnings`. Report only the warnings:

- `no-recent-activity`, `no-next`: ask whether to add a next step now
  (`- [ ] <step> #next 📅 [<date>]` in the home note) or leave it.
- `review-overdue`: suggest running `project-review` on that project
  later. Don't review projects here.
- `no-home-note`: mention it.

### 5. `#later` scan

Run `meta-notes tasks --all --later --tag later --json` and show the
tasks in batches of about ten. For any the user says is now live, run
`meta-notes task update <file>:<line> --expect '<text>' --remove-tag later`
plus `--due <date>` if it needs one, for example
`--remove-tag later --due 2026-10-02`.

### 6. Write the summary

Run `meta-notes note weekly` to get (or create) this week's weekly note.
Write under its `## Review` section (add the heading before `## Notes` if
missing), in two parts and nothing else:

```markdown
## Review

### This week

- <what was done> — <why it matters>

### Coming up

- <YYYY-MM-DD>: <important date or deadline>
```

Draft "This week" from completed tasks, time, notes, and the changed
notes the user kept, grouped by project or theme, 3–7 bullets. Draft
"Coming up" from
`meta-notes tasks --tag deadline --all --json` and dated tasks due in the
next few weeks that others care about. Show the draft, apply the user's
edits, then write it.

### 7. Mark and hand off

Find `review complete` with `grep -n` in the weekly note (add
`- [ ] review complete` under the Quarterly Plan link if missing) and
check it with `meta-notes task update ... --status x`.

Then remind the user: "Weekly planning is next, usually Friday
afternoon (`weekly-plan`)." Don't start it.

## Stopping early

When the user says stop: save what's decided (task updates, a partial
summary if one was approved), list the steps not done, leave
`review complete` unchecked, and end without further questions.
