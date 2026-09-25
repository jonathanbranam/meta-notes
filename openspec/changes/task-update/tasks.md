## 1. Shared task rules

- [ ] 1.1 In `scripts/tasks.py`, add module-level `CHECKBOX_PATTERN` and `is_task(text)` and use them in `find_tasks_in_file`; verify `pipenv run pytest test/unit/test_tasks.py test/unit/test_find_tasks.py` passes unchanged and new `test_is_task_*` tests cover due emoji, bare emoji, `🛫` date, and plain checkbox

## 2. Line editor (`scripts/meta_notes/task_update.py`)

- [ ] 2.1 Add `update()`, `UpdateResult`, and `TaskUpdateError` with file reading that keeps line endings and the final newline, the `--expect` check ignoring trailing whitespace (error carries `current`), the checkbox and line-range checks, and no write when the line is unchanged; verify with `test/unit/test_task_update.py` tests for mismatch, trailing whitespace, out of range, not a checkbox, CRLF, no final newline, and unchanged file mtime
- [ ] 2.2 Add marker token helpers (date marker with optional `️` and shape-matched date, removal that takes the preceding space or the following space after the checkbox, insertion in `🛫`, due, `✅` order); verify with unit tests for removal spacing and insertion order
- [ ] 2.3 Implement `--due` (date, `undated`, `none`; existing emoji kept, new emoji `📅`); verify with tests for each spec scenario under "Set the due date", including 📆 and 🗓 lines and an invalid date after the emoji
- [ ] 2.4 Implement `--start` (date, `none`); verify with tests for the "Set the start date" scenarios
- [ ] 2.5 Implement `--status` with ✅ handling: stamp on a change to done unless ✅ exists, the post-edit due date is today, or `no_completed`; remove every ✅ for any other status; leave done-to-done unchanged; verify with tests for each "Completion date" scenario using a fixed `today`
- [ ] 2.6 Implement tag removal and addition with `tags.TAG_PATTERN` and `canonical_tag` (case and aliases), added tags before the first date emoji or at the end, and no-ops for present or absent tags; verify with tests for each "Add and remove tags" scenario
- [ ] 2.7 Add the warning when an edit makes `is_task` false for a line that was a task; verify with a `--due none` test and a test that a plain checkbox edit without dates adds no warning

## 3. CLI (`meta-notes task update`)

- [ ] 3.1 Add the `task` subcommand group with `update` in `cli.py`: target split on the last `:`, `to_root_relative`, `--expect` required, `--status` choices, `--due`/`--start` format checks, tag name checks, add/remove conflict, and at least one edit option; verify with `test/unit/test_cli.py` tests for each usage error
- [ ] 3.2 Add `cmd_task_update` output: text `<file>:<line>` with `- old` and `+ new` lines or `unchanged`, JSON `file`, `line`, `old`, `new`, `changed`, `warnings`, and `current` on a mismatch; verify with CLI tests for text, JSON success, and JSON mismatch
- [ ] 3.3 Run the command against a temporary notes root from a shell (status, tag, due, start, and a mismatch) and verify the file contents and `git diff` show only the target lines changed

## 4. Docs and skills

- [ ] 4.1 Add `meta-notes task update` to `doc/meta-notes.txt` (`*meta-notes-cli-task-update*`, options, ✅ rule, `>` semantics, JSON fields) and to README's Command Line examples; verify `:helptags doc` succeeds and the tag resolves
- [x] 4.2 In `doc/meta-notes.txt` and `docs/planning-system.md`, write new tasks with `📅` (dated and bare) while noting 📆 and 🗓 are still read; verify with `grep -n '📆' doc docs` showing only "also accepted" mentions
- [ ] 4.3 Update `skills/project-review/SKILL.md`: step 7 edits task lines with `meta-notes task update` using `file`, `line`, and `text` from `meta-notes tasks --json`, the intro no longer lists `task update` as pending, and tag examples put tags before the date (`... #next 📅 <date>`); verify by reading the skill end to end

## 5. Verification

- [ ] 5.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh --quiet` and verify both pass
- [ ] 5.2 Run `openspec validate task-update --strict` and verify it passes
