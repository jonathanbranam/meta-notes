---
name: weekly-plan
description: Plan next week in a meta-notes notes root (Monday–Friday, usually Friday afternoon; all seven days on Sunday in a personal root), about 30 minutes. Use when the user says "weekly plan", "plan next week", or follows the reminder at the end of weekly-review. Works out capacity from next week's calendar, lists deadlines and meetings to schedule, and writes 3–5 priorities into next week's note. It does not review this week (that is weekly-review).
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
2. Run `meta-notes conventions` and follow it for everything below. If
   it ends with a "Personal mode" section, this is a personal root; steps
   that differ say so.

## Hard rules

- The target is next week, Monday to Friday (NEXT_MON..NEXT_FRI), unless
  the user names another week. In a personal root the plan is made on
  Sunday and covers Monday to Sunday (NEXT_MON..NEXT_SUN); read
  NEXT_MON..NEXT_FRI below as NEXT_MON..NEXT_SUN, and list all seven days.
- Change existing task lines only with `meta-notes task update`, with
  `file`, `line`, and `text` from `meta-notes tasks --json`. Never rewrite
  them by hand.
- Assign work to days only roughly; `daily-plan` plans each day in detail
  (the Time Block).
- Don't read git history or file modification times.
- If the user says stop, go to "Stopping early".

## Steps

### 1. Read the review

Run `meta-notes ceremony status --json`. If `weekly-review` is not done,
say so in one line and continue. Read the `## Review` section of this
week's weekly note (the `weekly-review` entry's `note`).

### 2. Calendar and capacity

Run `meta-notes calendar --date NEXT_MON..NEXT_FRI --json`.

- `ok` true: use its `days` as next week's meetings. Tell the user in one
  line how old the export is (`source.age_days`) and pass on each of its
  `warnings` (a stale or missing export, `email` not set). Don't ask for a
  screenshot.
- `ok` false because calendar support isn't installed: tell the user to
  run `meta-notes init` in the notes root (the error names the exact
  command), and offer to continue from a screenshot of next week's
  calendar.
- `ok` false otherwise (for example, no export): tell the user they can
  export from Google Calendar (Settings, Import & export, Export) and save
  the `.zip` into the `ics/` folder the error names, then you'll re-run
  the command, or provide a screenshot of next week's calendar. Continue
  with whichever they provide.

Ask for working hours if you don't know them (assume 8:00–17:00
otherwise; in a personal root the day is 7:00–21:00, from
`meta-notes prime`).

The capacity threshold is the shortest free gap that counts. Read it from
the notes root's `CLAUDE.md`, where the user keeps their preferences (a
line such as `Capacity gap: 30 minutes`); it wins over this skill. If
`CLAUDE.md` has no threshold, ask the user for theirs, suggesting 30
minutes, and once they answer, add the line to `CLAUDE.md` so the next run
reads it. If they have no preference, use 30 minutes and say so.

For each day, list:

- meetings
- free gaps of the threshold or more: these are capacity. Gaps between the
  threshold and 60 minutes are usable but tighter (fine for short tasks,
  not deep work); call them out as tighter.
- shorter free gaps are back-to-back transition buffers: don't count or
  list them

Total the capacity per day and for the week. For example, a 2-hour and a
45-minute gap on Tuesday give 2.75 hours of capacity, with the 45-minute
gap called out as tighter. Keep each day's capacity; step 4 assigns work
to days by it.

### 3. Deadlines and meetings to schedule

- Deadlines: `meta-notes tasks --tag deadline --all --json` and
  `meta-notes tasks --due --date NEXT_MON..NEXT_FRI --json`, landing in
  NEXT_MON..NEXT_FRI.
- Meetings to schedule: ask, and look for them in the review and in
  `meta-notes tasks --all --tag wait --json`.

### 4. Priorities

Propose 3–5 priorities from the review, deadlines, and project `#next`
tasks (`meta-notes tasks --all --tag next --json`). Let the user choose.
Then make a rough first pass at the days: assign each priority and each
deadline to the specific days that have capacity for it, by its rough size
and urgency, without overfilling any day (a deadline's work lands on or
before its date). It needn't be precise; `daily-plan` and `daily-shutdown`
keep it current as the week unfolds. Show the user the per-day result and
let them adjust it.

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

### Mon 2026-10-05

- [ ] <work assigned to Monday> (from Priority 1)

### Tue 2026-10-06

- [ ] <work assigned to Tuesday> (deadline <what>)
```

Each day's capacity counts the free gaps at or above the threshold from
step 2, so the per-day numbers follow the user's setting. The per-day
breakdown is the part the other skills use: one
`### <Weekday> <YYYY-MM-DD>` heading per day of the plan's week (Monday to
Friday; all seven days in a personal root), each with checklist lines,
after the week-level sections. A day with no work still gets its heading.
The lines point at the priorities and deadlines above; don't repeat their
prose. Write the section with `meta-notes note write` (see
`meta-notes note write --help`), never by editing the file directly.

### 6. Mark

Find `plan complete` with `grep -n` in next week's note (add
`- [ ] plan complete` under the Quarterly Plan link if missing) and check
it with `meta-notes task update ... --status x`. Tell the user
`daily-plan` will read this plan every day, and `daily-shutdown` will keep
the per-day breakdown current.

## Stopping early

When the user says stop: write whatever parts of the plan are decided,
list what's left, leave `plan complete` unchecked, and end without
further questions.
