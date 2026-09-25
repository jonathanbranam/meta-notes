---
name: project-review
description: Review ONE meta-notes project in 5–10 minutes, monthly, to decide whether it continues, pauses, is done, or becomes an area. Use when the user asks to review a project, says "project review", "next project", or "review <project>". Never reviews more than one project per run. It doesn't clean up stale or overdue tasks (task-cleanup) or plan a day or week.
---

# Project Review

Decide what happens to one project and record that it was reviewed. The
user usually has 5–10 minutes between meetings: be brief, ask one thing
at a time, and save what's decided if the user stops.

## Time budget

5–10 minutes for one project. Say so in one line when you start.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it for everything below.

## Hard rules

- One project per run. Never list or propose other projects to review.
- Don't walk through the project's old tasks one by one. That is
  `task-cleanup`; suggest it if the open list is long and stale.
- Change existing task lines only with `meta-notes task update`, with
  `file`, `line`, and `text` from `meta-notes project brief --json`. If
  it says the line changed, re-run the brief and retry, or ask. Never
  rewrite a task line by hand.
- Set fields (`status`) and add new lines by editing the home note
  directly, tags before date markers, lines within 80 columns.
- Run `meta-notes archive`, `move`, and `note new` only after the user
  confirms the exact command, and only in step 6, after the review is
  recorded. Never use `mv` or `git mv`.
- Don't read git history, `git blame`, or file modification times. The
  brief's `latest_date` and task dates are the signal of activity.
- If the user says stop, go to "Stopping early".

## Steps

### 1. Pick the project

If the user named one, use it, whatever its status.

Otherwise run `meta-notes projects --json`. Leave out projects with
status `done`. Pick the one with `last_review` null; if none, the oldest
`last_review`; ties go to the first in the list. Run step 2's brief on
it: if `scheduled_reviews` has a task due after today, the user asked to
wait, so pass over it and take the next candidate. Say which project
you're reviewing in one line. Don't show the list.

### 2. Gather

```sh
meta-notes project brief <path> --json
```

The result is under `project`: `home`, `status`, `tag`, `fields`,
`latest_date`, `last_review`, `has_next`, `warnings`, `files`, `open`,
`later`, `deadlines`, `scheduled_reviews`, `completed` (the last 90 days,
`--since <YYYY-MM-DD>` for more), and `completed_total`. Read the home
note. Open other files only if the home note doesn't explain the
project.

### 3. State (about ten lines)

Show the files and the tasks, open and completed, then:

- What the project is, in one sentence
- Status, tag, deadlines, and scheduled reviews
- Latest date and last review (or never)
- Open tasks, `#later` tasks, and completed (listed of total)
- Whether there's an open `#next`
- Anything that looks off: a deadline passed, no activity in months, a
  `no-home-note` warning

Ignore warnings on a project in `archive/project/`.

### 4. Disposition

Ask the user to choose one:

- **Continue**: still active. No field change.
- **Pause**: set `status: paused`. Offer to add
  `- [ ] Reconsider project #review 📅 <YYYY-MM-DD>` for when to look
  again; selection skips the project until then.
- **Done**: set `status: done`. Offer `meta-notes archive <path>` for
  step 6. If the user declines, it stays in `project/`; selection skips
  `done` projects.
- **Convert to area**: it has become an ongoing responsibility. Offer
  `meta-notes move <path> area/<name>` for step 6.
- **Split**: part of it is its own project. Offer
  `meta-notes note new project/<name>` for the new home note (add a title
  and `- status: active` if the note lacks them), and carry the tasks
  that belong there (step 5).
- **Merge**: it belongs in another project. Carry its tasks to that
  project's home note (step 5), and offer
  `meta-notes move <path> <other-project>/<name>` or
  `meta-notes archive <path>` for what's left.

Set fields by editing the field list in the home note: replace the
`- status:` item, or add one after the title if there's no field list.

### 5. Next action and carried tasks

- If the project stays active (continue, split, or the kept side of a
  merge) and `has_next` is false, ask for one concrete next action and
  write `- [ ] <action> #next 📅 [<YYYY-MM-DD>]` in the home note. If the
  user doesn't want one, accept that. Don't ask for paused, done, or
  converted projects.
- For each task carried to another project, write the copy in the
  target note, then mark the original
  `meta-notes task update <file>:<line> --expect '<text>' --status '>'`.
  Don't change the original's dates.

### 6. Record, then restructure

Record the review in the home note before any `archive` or `move`:

1. In the brief's `open`, find `#review` tasks in the home note that are
   undated or due on or before today. Check off the earliest:
   `meta-notes task update <file>:<line> --expect '<text>' --status x`.
   Leave `#review` tasks due after today open.
2. If there's none, add `- [ ] project #review 📅` to the home note,
   under its other `#review` lines, or after the field list if it has
   none. Re-run `meta-notes project brief <path> --json`,
   find that line in `open`, and check it off the same way. The result
   is `- [x] project #review 📅 ✅ <today>`.

If a folder project has no home note, offer to create `<path>Home.md`
with a `# <Title>` line and a field list (`- status: <status>`, and
`- tag:` if the user gives one), then record there. If the user
declines, say the review wasn't recorded.

Then show each structural command offered in step 4 and run it after
the user confirms it. `archive` sets `status: archived` and the
`archived` date itself. If the user would rather wait, add a task to the
home note instead, for example
`- [ ] Convert to area: meta-notes move <path> area/<name> #next 📅`.

### 7. Close

Summarize in three lines: disposition, tasks changed, next action.
Don't commit; commits happen at shutdown.

## Stopping early

When the user says stop: apply what's decided (fields and task updates),
record the review as in step 6, and add
`- [ ] Finish project review #review 📅 <next workday>` to the home note
(Monday to Friday; on Friday 2026-09-25, `📅 2026-09-28`). Skip
structural commands not yet confirmed. List what was left undone and end
without further questions.
