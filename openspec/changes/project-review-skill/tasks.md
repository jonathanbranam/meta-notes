## 1. Prerequisites

- [ ] 1.1 Confirm `project-brief` and `planning-skills` are archived: `meta-notes project brief`, `meta-notes projects`, and `meta-notes conventions` run, and `skills/task-cleanup/SKILL.md` exists; if not, stop; verify by running each command in a scratch notes root

## 2. Skill

- [ ] 2.1 Revise `skills/project-review/SKILL.md` in the shared skill shape: `meta-notes conventions` first, selection from `meta-notes projects --json` (never-reviewed, then oldest `last_review`), `meta-notes project brief --json` for state, dispositions setting the `status` field, `meta-notes archive`/`move` after confirmation, no stale-task walk, recording the review as a completed `#review` task, early stop, and a description that doesn't trigger on task cleanup; verify by reading it against "Project review" and its scenarios
- [ ] 2.2 Check the skill against the shared `ceremony-skills` requirements ("Skills start from the CLI", "Edits go through the CLI", "Time budget and stopping early"): no direct task-line rewrites, no git history, `git blame`, or mtime use, tags before dates, lines within 80 columns; verify by reading it and fixing any gaps

## 3. Docs

- [ ] 3.1 Update the project review section of `docs/planning-system.md` to match the skill; verify by reading it against the spec

## 4. Verification

- [ ] 4.1 In a scratch notes root with a never-reviewed project and a reviewed one, walk through `project-review` with a fixed date and verify it picks the never-reviewed project, every edit went through `task update` or a confirmed command, and the home note gains a completed `#review` line
- [ ] 4.2 Run `openspec validate project-review-skill --strict` and verify it passes
