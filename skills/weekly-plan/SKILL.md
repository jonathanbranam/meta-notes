---
name: weekly-plan
description: Plan next workweek (Monday–Friday) in a meta-notes notes root, usually Friday afternoon, about 30 minutes. Use when the user says "weekly plan", "plan next week", or follows the reminder at the end of weekly-review. Works out capacity from a calendar screenshot, lists deadlines and meetings to schedule, and writes 3–5 priorities into next week's note. It does not review this week (that is weekly-review).
---

# Weekly Plan

Turn the weekly review and next week's calendar into a short plan:
capacity, deadlines, and 3–5 priorities placed roughly on days.

## Time budget

About 30 minutes. Say so in one line when you start.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.

## Hard rules

- The target is next week, Monday to Friday (NEXT_MON..NEXT_FRI), unless
  the user names another week.
- Change existing task lines only with `meta-notes task update`, with
  `file`, `line`, and `text` from `meta-notes tasks --json`. Never rewrite
  them by hand.
- Don't plan individual days in detail; `daily-plan` does that.
- Don't read git history or file modification times.
- If the user says stop, go to "Stopping early".

## Steps

### 1. Read the review

Run `meta-notes ceremony status --json`. If `weekly-review` is not done,
say so in one line and continue. Read the `## Review` section of this
week's weekly note (the `weekly-review` entry's `note`).

### 2. Calendar and capacity

Ask for a screenshot of next week's calendar. Ask for working hours if
you don't know them (assume 8:00–17:00 otherwise). For each day, list:

- meetings
- free gaps of 90 minutes or more: these are capacity
- shorter free gaps, listed separately; they aren't capacity

Total the capacity per day and for the week. For example, a 2-hour and a
45-minute gap on Tuesday give 2 hours of capacity and one short gap.

### 3. Deadlines and meetings to schedule

- Deadlines: `meta-notes tasks --tag deadline --all --json` and
  `meta-notes tasks --due --date NEXT_MON..NEXT_FRI --json`, landing in
  NEXT_MON..NEXT_FRI.
- Meetings to schedule: ask, and look for them in the review and in
  `meta-notes tasks --all --tag wait --json`.

### 4. Priorities

Propose 3–5 priorities from the review, deadlines, and project `#next`
tasks (`meta-notes tasks --all --tag next --json`). Let the user choose.
Place each roughly on days that have capacity, without overfilling any
day.

### 5. Write the plan

Run `meta-notes note weekly <NEXT_MON>` to get (or create) next week's
note. Write under its `## Plan` section (add the heading before
`## Notes` if missing):

```markdown
## Plan

Capacity: <n> h (Mon <n>, Tue <n>, Wed <n>, Thu <n>, Fri <n>)

### Priorities

1. <priority> (Mon, Tue)

### Deadlines

- <YYYY-MM-DD>: <deadline>

### To schedule

- <meeting>

### Short gaps

- Tue 10:15–11:00
```

### 6. Mark

Find `plan complete` with `grep -n` in next week's note (add
`- [ ] plan complete` under the Quarterly Plan link if missing) and check
it with `meta-notes task update ... --status x`. Tell the user Monday's
`daily-plan` will read this plan.

## Stopping early

When the user says stop: write whatever parts of the plan are decided,
list what's left, leave `plan complete` unchecked, and end without
further questions.
