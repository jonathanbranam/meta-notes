---
name: project-review
description: Review ONE meta-notes project in 5–10 minutes. Use when the user asks to review a project, reconcile projects, clean up stale tasks, or says "next project" or "review <project>". Never review more than one project per invocation.
---

# Project Review

Reconcile a single project so its state is current enough to plan against.
The user usually has 5–10 minutes between meetings. Respect that: be brief,
ask one thing at a time, and save progress whenever the user stops.

This draft uses the tools that exist today (the `meta-notes` CLI, git,
grep). `meta-notes` is on `PATH`; run it from anywhere in the notes root.
When `meta-notes project brief` and `meta-notes task update` land, replace
steps 2 and 7 with those commands.

## Hard rules

- One project per invocation. Never list or propose other projects to review.
- Never edit a file without the user's decision for that item.
- If the user says stop, go to step 8 immediately.
- Move, rename, or archive only with `meta-notes move`, `rename`, or
  `archive`, which update links, and only after the user confirms that
  exact command. Never use `mv` or `git mv`.
- Keep task lines within 80 columns.

## Syntax reference

- Task: a checklist line with `📅` (dated or bare) or `🛫 YYYY-MM-DD`
- Status: space open, `x` done, `>` rescheduled, `-` canceled; `.`, `o`, `O`
  partial
- Completion: append `✅ YYYY-MM-DD` when marking done, never when canceling
- `#later`: someday/maybe, excluded from active lists
- `#next`: the project's next action
- Links: `[[path/without/extension]]`, relative to the notes root

## Steps

### 1. Pick the project

If the user named one, use it. Otherwise choose the project in `project/`
whose index note has the oldest `reviewed:` frontmatter date, treating a
missing date as oldest. For a folder project the index note is `index.md`,
or the note named after the folder if there's no `index.md`. State which
project you picked in one line.

### 2. Gather (quietly, with commands, not by reading every file)

- Files: `git ls-files project/<name>` and sizes.
- Last meaningful change per file:
  `git log -1 --format=%as --follow -- <file>`. Uncommitted changes count
  as today (`git status --porcelain`).
- Open tasks inside:
  `meta-notes tasks --folder project/<name> --json`
- Open tasks elsewhere: grep for `[[project/<name>` and for the project's
  `tag:` (if set), limited to checklist lines. `meta-notes tasks` has no
  tag filter yet.
- Task age: `git blame --porcelain` on files with open tasks. The author
  date of a task's line is its last-edited date.
- Time data: the most recent daily note mentioning the tag or link.

Read the index note. Open other files only if the index doesn't explain the
project.

### 3. State (about ten lines)

- What the project is, in one sentence (the `outcome:` if present)
- Status, deadline, and `revisit:` if present
- Last meaningful change and last logged time
- Open tasks: count inside, count elsewhere, count older than 30 days
- Whether there's an open `#next`
- Anything that looks off (deadline passed, no activity in months)

### 4. Disposition

Ask the user to choose one:

- **Continue**: still active
- **Pause**: set `status: paused`, optionally with `revisit:`
- **Done**: set `status: done`; archive later
- **Convert to area**: it has become an ongoing responsibility
- **Split or merge**: parts belong in other projects

For anything other than continue or pause, go to step 6 afterwards and keep
the task walk short.

### 5. Stale tasks

Present open tasks oldest first, in batches of up to 8, one line each with
its age. For each batch, offer: keep, date it, `#later`, cancel, or done.
Offer "cancel all" or "later all" for a batch when most are very old. Stop
the walk when the user signals time is short.

### 6. Next action and capture

- If there's no open `#next`, ask for one concrete next action. If the user
  doesn't want one, accept that; it's a warning, not a rule.
- Ask once: "Anything else you owe, are waiting on, or need to do here?"
  Capture answers as task lines.

### 7. Apply

- Edit task lines directly: status character, tags, dates, ✅ date.
- New tasks go in the project's index note unless the user says otherwise.
- Frontmatter: set whatever changed (`status`, `revisit`, `outcome`) and
  stamp `reviewed: <today>`. Add frontmatter if the note has none.
- Structural changes (archive, convert to area, split): offer to run the
  command now, for example `meta-notes move project/x area/x` or
  `meta-notes archive project/x`. If the user would rather wait, add a task
  to the index note instead, for example
  `- [ ] Convert to area: meta-notes move project/x area/x 📅 <date> #next`.
  Run structural commands last, after the other edits in this step.

### 8. Close

Summarize in three lines: disposition, tasks changed, next action. If the
user stopped early, stamp `reviewed:` anyway and add `- [ ] Finish project
review 📅 <today+1>` to the index note, so it comes up next time.

Don't commit. Commits happen at shutdown.
