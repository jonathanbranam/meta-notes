## Context

`skills/project-review/SKILL.md` is a draft written against the tools that
existed before the CLI: it lists files with git, finds tasks with
`find_tasks.py` and grep, estimates age with `git blame`, and walks the
project's stale tasks. `planning-skills` defines the shared skill shape
and requirements and ships `task-cleanup`; `project-brief` adds
`meta-notes project brief`.

## Goals / Non-Goals

**Goals:**
- Every read is `meta-notes conventions`, `meta-notes projects`, or
  `meta-notes project brief`; every edit is `task update`, a direct field
  or line edit, or a confirmed `archive`/`move`.
- The skill judges the project; the commands supply the facts.

**Non-Goals:**
- Git history, `git blame`, or file mtimes (`task-age` is deferred).
- Reviewing areas.
- Working through old tasks; that is `task-cleanup`.

## Decisions

### Selection from `meta-notes projects`

With no project named, the skill runs `meta-notes projects --json`,
leaves out `done` projects (they're waiting to be archived, and
`review-overdue` skips them too), and picks the entry with no
`last_review`, then the oldest, ties in list order. It doesn't show the
list, so it never proposes other projects.

`projects` doesn't report scheduled reviews, so the skill checks the
picked project's brief: an open `#review` due after today (a paused
project's reconsider date, or a stopped review's follow-up) means the
user asked to wait, and the skill takes the next candidate. That costs an
extra `project brief` only when a pick is passed over. A named project is
always reviewed.

*Alternative:* `project brief` on every project. That repeats the task
parse per project, which `projects` avoids.

### State from one `project brief` call

Step 2 is `meta-notes project brief <path> --json`. The skill summarizes
fields, files, open and completed tasks, `#later`, `#deadline`, and
`has_next` in about ten lines.

### Dispositions

Pause and done set `status` by editing the field list directly, as
"Edits go through the CLI" allows. Done offers `meta-notes archive` at
once; declining leaves a `done` project in `project/`, which selection
skips. Convert to area is a `meta-notes move` to `area/`. Split and merge
carry tasks with the "Carrying a task forward" rule (copy, then mark the
old line `>`), create new project notes with `meta-notes note new`, and
move notes with `meta-notes move`. The skill asks for a next action only
when the project stays active, the same condition as `no-next`.

### Recording the review

The review is a completed `#review` task in the home note. An open
`#review` in the home note that is undated or due on or before today is
checked off with `task update --status x`, the earliest first. Otherwise
the skill adds `- [ ] project #review 📅`, re-runs `project brief --json`
to get the new line's `file`, `line`, and `text`, and checks it off the
same way, so the ✅ date comes from the CLI. Open `#review` tasks due
after today are reminders the user set and stay open.

A folder project without `Home.md` has nowhere to record the review; the
skill offers to create one (title and field list) and otherwise says the
review wasn't recorded.

### Order of edits

Fields and the `#review` record are written first; confirmed `archive`
and `move` commands run last. `archive` and `move` change the home
note's path, and `archive` sets `status: archived` itself.

## Risks / Trade-offs

- [`project brief` output changes before this lands] → The skill is
  written after `project-brief` is archived, against its real output.
- [Large projects produce long briefs] → The skill summarizes, and the
  brief lists completed tasks from the last 90 days only (`--since` for
  more).
- [A stopped review counts as a review] → It resets `last_review`, so
  selection won't pick the project again; the open `#review` dated the
  next workday brings it back through daily planning's due tasks.

## Migration Plan

1. Wait for `project-brief` and `planning-skills` to be archived.
2. Rewrite the skill, then the docs.
3. `init` links skills, so existing notes roots see the new skill without
   re-running it.
4. PATCH version bump on archive; tag `v<version>`.
