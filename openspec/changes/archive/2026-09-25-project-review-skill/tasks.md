## 1. Prerequisites

- [x] 1.1 Confirm `project-brief` and `planning-skills` are archived: `meta-notes project brief`, `meta-notes projects`, and `meta-notes conventions` run, and `skills/task-cleanup/SKILL.md` exists; if not, stop; verify by running each command in a scratch notes root

## 2. Skill

- [x] 2.1 Revise `skills/project-review/SKILL.md` in the shared skill shape: `meta-notes conventions` first, selection from `meta-notes projects --json` (skip `done`, never-reviewed then oldest `last_review`, pass over a pick with an open `#review` due after today), `meta-notes project brief --json` for state, and a description that doesn't trigger on task cleanup; verify by reading it against "Project review" and "Project review selection" and their scenarios
- [x] 2.2 Write the disposition step: pause and done set `status`, pause offers a dated `#review`, done offers `meta-notes archive`, convert uses `meta-notes move`, split and merge carry tasks forward and use `note new` and `move`, every structural command after confirmation, a next action asked only when the project stays active, and no stale-task walk; verify by reading it against "Project review disposition" and its scenarios
- [x] 2.3 Write the record and close steps: check off an undated or due open `#review` in the home note, or add `- [ ] project #review 📅` and check it off using the line from a fresh `project brief --json`; leave future `#review` tasks open; offer to create `Home.md` when missing; write fields and the record before any `archive` or `move`; on early stop, record the review and add a `#review` task dated the next workday; verify by reading it against "Project review record" and its scenarios
- [x] 2.4 Check the skill against the shared `ceremony-skills` requirements ("Skills start from the CLI", "Edits go through the CLI", "Carrying a task forward", "Time budget and stopping early"): no direct task-line rewrites, no git history, `git blame`, or mtime use, tags before dates, lines within 80 columns; verify by reading it and fixing any gaps

## 3. Docs

- [x] 3.1 Update the project review section of `docs/planning-system.md` to match the skill; verify by reading it against the spec
- [x] 3.2 Check that README's Planning Skills table and the `ceremony-skills` Purpose name `project-review`; verify by reading both after archiving syncs the spec

## 4. Verification

- [x] 4.1 In a scratch notes root with a never-reviewed project, a never-reviewed `done` project, a reviewed one, and one with a `#review` due after today, walk through `project-review` with a fixed date and verify it picks the never-reviewed active project, every edit went through `task update` or a confirmed command, and the home note gains a completed `#review` line
- [x] 4.2 In the same root, walk through done with archive and verify the `status` and `#review` lines are written before `meta-notes archive` runs and appear in `archive/project/`
- [x] 4.3 In the same root, stop a review before the disposition and verify the home note has a completed `#review` for today and an open `#review` dated the next workday
- [x] 4.4 Run `openspec validate project-review-skill --strict` and verify it passes

## 5. Release

- [x] 5.1 Bump `__version__` PATCH in `scripts/meta_notes/__init__.py` when archiving the change, tag `v<version>`; verify `meta-notes --version`
