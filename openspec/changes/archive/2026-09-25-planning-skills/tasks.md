## 1. Shared rules

- [x] 1.1 Confirm `scripts/meta_notes/project.py` (from `archive-project-status`) provides `home_note` and `read_fields`; verify by importing the module and running `pipenv run pytest test/unit/test_project.py`
- [x] 1.2 Add `#waiting` → `#wait` to `TAG_ALIASES` in `scripts/tags.py`; verify with `test/unit/test_tags.py` and `test_find_tasks.py` tests for the "Waiting alias" scenario (`--tag wait` and `--tag waiting` both select `#waiting`), and a `test_time_tracking.py` test that `#waiting` time totals under `#wait`
- [x] 1.3 Rename `tasks._char_to_status` to public `char_to_status` and add a module-level status table (character → meaning) beside `DUE_EMOJIS`; verify `pipenv run pytest test/unit/` passes unchanged

## 2. `meta-notes conventions`

- [x] 2.1 Write `scripts/meta_notes/conventions.md` covering every item in the "Conventions content" requirement, with `<!-- generated: statuses -->`, `<!-- generated: due-emoji -->`, and `<!-- generated: tag-aliases -->` markers; verify by reading it against the spec's list
- [x] 2.2 Add `scripts/meta_notes/conventions.py` that fills the markers from `tasks.py` and `tags.py`, and the `conventions` subcommand in `cli.py` with `resolves_root` false and JSON `version` and `text`; verify with `test/unit/test_conventions.py` (every marker replaced, every `TAG_ALIASES` entry listed including `#waiting`, all three due emoji with 📅 as the one to write) and `test_cli.py` tests for running outside a notes root and `--json`

## 3. `meta-notes ceremony status`

- [x] 3.1 Add `scripts/meta_notes/ceremony.py`: marker matching with `CHECKBOX_PATTERN` (case and whitespace ignored, trailing ✅ stripped and reported, done only for `x`/`X`, any done line wins), note paths from `note.periodic_note`, and missing note or marker reported as not done; verify with `test/unit/test_ceremony.py` tests for each "Ceremony markers" scenario
- [x] 3.2 Add the `ceremony` subcommand group with `status` in `cli.py`: `--date` checked as a single `YYYY-MM-DD` (range and month are usage errors), text lines with `(no note)`/`(no marker)`, and JSON `date`, `week_start`, `ceremonies`; verify with CLI tests for the "All four ceremonies", "Missing weekly note", "Range rejected", and "JSON result" scenarios

## 4. `meta-notes projects`

- [x] 4.1 Add `scripts/meta_notes/projects.py` listing `project/*.md` and `project/*/` (home note `Home.md`, `no-home-note` warning, archive excluded, sorted by path) and reading fields through `project.py`; verify with `test/unit/test_projects.py` tests for the "Projects listed" and "Project fields" scenarios
- [x] 4.2 Assign tasks to projects from one `find_tasks.collect_tasks` pass, by path and by canonical tag, and compute last review from completed `#review` tasks; verify with tests for "Project tasks" and "Last review" scenarios, including a scheduled review not yet done
- [x] 4.3 Add the latest-date scan (valid `YYYY-MM-DD` in file paths, file contents, and tagged task text, on or before today; no git or mtimes); verify with tests for "Dated meeting note", "Future due date ignored", and "Tagged task elsewhere counts", plus an invalid date such as `2026-02-30` being skipped
- [x] 4.4 Add the `no-next`, `no-recent-activity`, and `review-overdue` warnings with a 30-day threshold and a fixed `today`; verify with tests for "Paused project" and "Stalled active project"
- [x] 4.5 Add the `projects` subcommand in `cli.py` with `--warnings` and JSON fields from "Project list output"; verify with CLI tests for "Only warnings" and "JSON result"

## 5. Templates

- [x] 5.1 Update `templates/daily.md` (markers under the Week Plan link, `## Follow Up` after `## Notes`) and `templates/weekly.md` (markers under the Quarterly Plan link, `## Review` and `## Plan` before `## Notes`), and regenerate the daily and weekly renderings in `test/fixtures/templates/`; verify with `test_template.py` tests for "New daily note" and "New weekly note", a test that `meta-notes tasks --all --status all` doesn't list the marker lines, and `./run_tests.sh test/init.vader`
- [x] 5.2 Check the markers end to end: render a daily note, check `shutdown complete` with `meta-notes task update --status x`, and run `meta-notes ceremony status`; verify it reports daily shutdown done with today's ✅ date

## 6. Skills

- [x] 6.1 Write `skills/daily-shutdown/SKILL.md` in the design's shared shape (budget, `meta-notes conventions` first, hard rules, numbered steps with exact CLI calls, stop section): collect, PR check, project next steps, the time-log check (time report, gaps and unclear stretches, questions, log updates), Follow up list, confirmed commit, marker, and the daily-plan offer; verify by reading it against the "Daily shutdown", "Ceremony completion and handoff", and "Time budget and stopping early" requirements
- [x] 6.2 Write `skills/daily-plan/SKILL.md`: target-day choice, previous workday's note, Monday weekly plan, calendar screenshot, due, overdue, and `#wait` tasks, `meta-notes note daily`, Plan column and first block, Follow up items tracked with `task update --due`, skipped-shutdown mention, marker, and no old-task walk; verify by reading it against "Daily planning" and its scenarios
- [x] 6.3 Write `skills/weekly-review/SKILL.md`: the Monday–Friday period, completed tasks and time report for that range, daily notes and Follow up lists, plan versus actual, commitments, `meta-notes projects --warnings`, the `#later` scan with `task update`, the two-part manager summary in `## Review` with no next-week plan, marker, and the weekly-plan reminder; verify by reading it against "Weekly review" and its scenarios
- [x] 6.4 Write `skills/weekly-plan/SKILL.md`: review and calendar screenshot, capacity (90-minute gaps, shorter gaps listed separately), meetings to schedule, `#deadline` and due dates, 3–5 priorities on days, next week's `## Plan` via `meta-notes note weekly`, and marker; verify by reading it against "Weekly planning"
- [x] 6.5 Write `skills/task-cleanup/SKILL.md`: overdue tasks oldest due first, then undated tasks by note, batches sized to the time given, per-task choices and cancel all / later all through `task update`, and stopping early; verify by reading it against "Task cleanup" and the "Later all" scenario
- [x] 6.6 Check every skill against the shared requirements ("Shipped skills", "Skills start from the CLI", "Edits go through the CLI", "Carrying a task forward"): no direct task-line rewrites, no git history or mtime use, tags before dates, lines within 80 columns; verify by reading all five and fixing any gaps

## 7. Docs

- [x] 7.1 Add `conventions`, `ceremony status`, and `projects` to `doc/meta-notes.txt` (with `*meta-notes-cli-...*` tags, options, and JSON fields) and to README's Command Line examples, and list the five new skills in README; verify `:helptags doc` succeeds and each new tag resolves
- [x] 7.2 Update `docs/planning-system.md` so the ceremonies, skills, and CLI sections match the shipped behavior (marker names, `meta-notes conventions`, the `projects` warnings); verify by reading it against the specs

## 8. Verification

- [x] 8.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh --quiet` and verify both pass
- [x] 8.2 In a scratch notes root with fixture projects, daily notes, and a weekly note, run `meta-notes init` and verify `.claude/skills/` links all five new skills; then run each command (`conventions`, `ceremony status`, `projects --warnings`) and verify the output matches the fixtures
- [x] 8.3 Walk through `daily-shutdown` and `weekly-review` in that scratch root with a fixed date and verify every edit went through `meta-notes task update` or a confirmed command and the markers read as done in `ceremony status`
- [x] 8.4 Run `openspec validate planning-skills --strict` and verify it passes
