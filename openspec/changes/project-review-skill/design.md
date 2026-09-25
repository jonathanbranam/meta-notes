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

With no project named, the skill runs `meta-notes projects --json` and
picks the entry with no `last_review`, then the oldest. It doesn't show
the list, so it never proposes other projects.

*Alternative:* `project brief` on every project. That repeats the task
parse per project, which `projects` avoids.

### State from one `project brief` call

Step 2 is `meta-notes project brief <path> --json`. The skill summarizes
fields, files, open and completed tasks, `#later`, `#deadline`, and
`has_next` in about ten lines.

### Recording the review

The review is a completed `#review` task in the home note. An open
`#review` task is checked off with `task update --status x`; otherwise the
skill adds `- [ ] project #review 📅` and checks it off the same way, so
the ✅ date comes from the CLI.

## Risks / Trade-offs

- [`project brief` output changes before this lands] → The skill is
  written after `project-brief` is archived, against its real output.
- [Large projects produce long briefs] → The skill summarizes; the
  completed-task window is `project-brief`'s open question.

## Migration Plan

1. Wait for `project-brief` and `planning-skills` to be archived.
2. Rewrite the skill, then the docs.
3. `init` links skills, so existing notes roots see the new skill without
   re-running it.
