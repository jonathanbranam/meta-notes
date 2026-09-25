## 1. Shared tag parser

- [x] 1.1 Create `scripts/tags.py` with `TAG_ALIASES`, the tag pattern `#([\w-]+)`, `canonical_tag(name)` (with or without `#`; returns the canonical name without `#`; alias lookup ignores case), and `parse_tags(text)` (canonical names in order, duplicates removed ignoring case). Add `test/unit/test_tags.py` covering several tags, tags before and after text, aliases, case, and duplicates; verify with `pipenv run pytest test/unit/test_tags.py`
- [x] 1.2 Make `time_tracking.Tag.__post_init__` use `tags.canonical_tag` (keeping the leading `#`), and import `TAG_ALIASES` from `tags` so `time_tracking.TAG_ALIASES` still resolves; verify `pipenv run pytest test/unit/test_time_tracking.py` passes unchanged

## 2. Shared period parser

- [x] 2.1 Create `scripts/period.py` with `parse_period(text, today=None) -> (start, end)` for `YYYY-MM-DD`, `START..END`, `YYYY-MM`, `YYYY-Qn`, `YYYY`, and `None` meaning today. Raise `ValueError` naming the value and listing the accepted forms for anything else, impossible dates, and reversed ranges. Add `test/unit/test_period.py` covering every scenario in `specs/date-period/spec.md` (including February, Q4, `next-month`, and `2026-W45`); verify with `pipenv run pytest test/unit/test_period.py`

## 3. Task model

- [x] 3.1 In `scripts/tasks.py`, accept 📅 as well as 📆 and 🗓 for the due date, and add `Task.undated` (a due emoji with no valid date after it), `Task.tags` (from `tags.parse_tags`), and the `effective_due` property (✅ date for a completed task that has one, else `due_date`). Verify with new `test_tasks.py` tests for each emoji, bare 📆, an invalid date after 📆, tags, and `effective_due` for completed, incomplete, and ✅-less tasks
- [x] 3.2 Make `find_tasks_in_file` keep only checkbox lines with a due emoji (dated or bare) or `🛫 YYYY-MM-DD`. Update the existing `test_tasks.py` and `test_find_tasks.py` fixtures that rely on plain checkboxes, and add tests showing a plain `- [ ]` line is skipped and a `🛫`-only line is kept; verify `pipenv run pytest test/unit/test_tasks.py`

## 4. Selection and report

- [x] 4.1 Add `find_tasks.select(tasks, modes, start, end, later)` implementing the predicates and section order in `design.md` (`--all` expands to ready, future, undated; no mode means ready; `#later` dropped unless `later`). Add `test_find_tasks.py` tests for every "Selection modes" and "Later tasks" scenario in `specs/task-query/spec.md`, the overlap rule (a task both overdue and ready is listed once, as overdue), and the ✅ rule; verify they pass
- [x] 4.2 Add a `--tag` filter (any of the given tags, compared as canonical names ignoring case) applied with `--status` and `--folder` before selection; verify with tests for a single tag, several tags, and an alias (`--tag mtg` matching `#meeting`)
- [x] 4.3 Replace `generate_report`, `generate_filtered_report`, and the week-bucket helpers with one report builder that uses the "Report layout" rules (no section heading for a single mode; `# Overdue` etc. for several; standard and condensed file formats; summary line; the existing empty-result messages). Verify with tests for the single-mode condensed scenario, the several-modes scenario, and the summary count
- [x] 4.4 Add `--group-by tag` to the report builder (`## <tag>` per tag sorted ignoring case, `## Not tagged` last, `### [[link]]` file headings in standard format, a task under each of its tags); verify with tests for both "Group by tag" scenarios
- [x] 4.5 Rewrite `find_tasks.main()` options: add `--date`, the seven mode flags, `--later`, repeatable `--tag`, and `--group-by {tag}`; keep `--folder`, `--status`, `--format`, and `--condensed`; drop `--due-on`, `--due-by`, and `--due-between`. Print invalid `--date` errors to stderr and exit 1. Update the module docstring and `--help` epilog. Verify with tests that `--due-on` is a usage error and `--date 2026-W45` exits 1 with the period error
- [x] 4.6 Remove `notes.calculate_week_end` and its tests once nothing imports it; verify with `grep -rn calculate_week_end scripts test` returning nothing and `pipenv run pytest test/unit/test_notes.py` passing

## 5. CLI

- [x] 5.1 Update `scripts/meta_notes/cli.py` `tasks` options to match `find_tasks.py` exactly, and `scripts/meta_notes/query.py` to call `select` once and build the text lines and JSON from the same results. Each JSON task gets `tags` and `section`, `category` is dropped, and a task appears once in JSON under `--group-by tag`. Verify with `test_query.py` and `test_cli.py` tests for both "Task query JSON" scenarios, the invalid `--date` JSON error, and text output equal to `find_tasks.py` for the default, `--all --folder project --status all`, `--overdue --due`, and `--group-by tag` runs

## 6. Templates

- [x] 6.1 In `templates/daily.md`, change "Tasks Due Today" to `--due --date {{date:%Y-%m-%d}} --condensed` and "Overdue Tasks" to `--overdue --date {{date:%Y-%m-%d}} --condensed` (dropping `--status incomplete`, which is the default). Copy the file over `test/fixtures/init_templates/daily.md`; verify with `diff templates/daily.md test/fixtures/init_templates/daily.md` and `pipenv run pytest test/unit/test_init.py`
- [x] 6.2 Update the `stub: find_tasks.py ...` lines in `test/fixtures/templates/daily-*.md` to the new arguments, and change the `--due-on` example in any template test to `--due --date`; verify `pipenv run pytest test/unit/test_template.py` passes
- [x] 6.3 Add a `test_template.py` test that a template calling `find_tasks.py --due-on <date>` renders the `<!-- Command failed: ...` comment containing the usage error and reports a warning; verify it passes
- [x] 6.4 In a scratch notes root with a dated task, a plain checkbox, and a `#later` task, run `bin/meta-notes note daily 2026-09-25 --render` and verify the task sections list only the dated, non-`#later` tasks

## 7. Documentation

- [x] 7.1 Update `doc/meta-notes.txt`: the `meta-notes tasks` options (`:help meta-notes-cli`), the `--date` forms, the task model (due emojis, bare 📆, plain checkboxes ignored, ✅ rule), tags and aliases, `#later` and `--later`, the JSON fields (`tags`, `section`, no `category`), the template example at line 362, and a migration note giving the replacements for `--due-on`, `--due-by`, and `--due-between`. Verify `:helptags doc` succeeds and each new tag opens
- [x] 7.2 Update the task options in `requirements.md` and the `tasks` examples in `README.md` to the new options; verify with `grep -rn "due-on\|due-by\|due-between" README.md requirements.md doc templates` returning only the migration note

## 8. Verification

- [x] 8.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh` and verify both pass
- [x] 8.2 Run `openspec validate find-tasks-enhancements --strict` and verify it passes
