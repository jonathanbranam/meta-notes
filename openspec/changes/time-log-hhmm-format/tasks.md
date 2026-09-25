## 1. Parser

- [ ] 1.1 Add failing tests to `test/unit/test_time_tracking.py`: `_parse_datetime` / `_parse_entry_time` accept `2026-02-14 08:00` (with and without a file date), and still reject `2026-02-14 8:00` and `2026-02-30 08:00`; verify the new acceptance tests fail with `pipenv run pytest test/unit/test_time_tracking.py`
- [ ] 1.2 Make the day abbreviation optional in the `_parse_datetime` regex (`(?:\s+\w{3})?\s+`) and verify the tests from 1.1 pass
- [ ] 1.3 Add `_parse_time_log_lines` tests for the spec's mixed-formats scenario, a full date that overrides the filename date (`* end: 2026-02-15 01:30` in a `2026-02-14` note), a mismatched day abbreviation, and a leftover `HH:MM` placeholder leaving the time unset while the entry is kept; verify they pass
- [ ] 1.4 Update the docstrings of `_parse_datetime`, `_parse_entry_time` and `_parse_time_log_lines` to list the four formats with bare `HH:MM` first, and verify the whole file passes with `pipenv run pytest test/unit/test_time_tracking.py`

## 2. Daily template

- [ ] 2.1 In `templates/daily.md`, change the starter entry to `  * start: HH:MM` and `  * end:   HH:MM`, and copy the file over `test/fixtures/init_templates/daily.md`; verify with `diff templates/daily.md test/fixtures/init_templates/daily.md` and `pipenv run pytest test/unit/test_init.py`
- [ ] 2.2 In `test/fixtures/templates/daily-2025-12-31.md`, `daily-2026-02-13.md` and `daily-2026-04-02.md` (if present; they come from `note-create`), replace the `* start: <date> <Ddd> HH:MM` / `* end:   <date> <Ddd> HH:MM` lines with `* start: HH:MM` / `* end:   HH:MM`; verify `pipenv run pytest test/unit/test_template.py` passes
- [ ] 2.3 Render a daily note with `bin/meta-notes note daily 2026-09-25 --render` in a scratch notes root and verify the starter entry has bare `HH:MM` and no date

## 3. Syntax highlighting

- [ ] 3.1 Add the anchored `metaNotesTime` match for `start:` / `end:` lines to `after/syntax/markdown.vim`, keeping the existing 12-hour pattern; verify with `./run_tests.sh` that nothing regresses
- [ ] 3.2 Convert the sample log in `test/syntax_test.md` to a mix of bare `HH:MM`, bare `3:20pm` and full-date timestamps; open it in Vim and verify each time is highlighted (`:echo synIDattr(synID(line('.'), col('.'), 1), 'name')` on each time reports `metaNotesTime`) and that an `HH:MM` in ordinary prose is not

## 4. Documentation

- [ ] 4.1 Add a time log format subsection under `*meta-notes-time-tracking*` in `doc/meta-notes.txt` that covers the `### Log` section, the activity line with tags, `start:` / `end:` / note detail lines, and the four timestamp formats (bare `HH:MM` first, date from the filename; unparseable values leave the time unset); verify `:helptags doc` succeeds and `:help meta-notes-time-tracking` shows it

## 5. Verification

- [ ] 5.1 Run `pipenv run pytest test/unit/` and `./run_tests.sh` and verify both pass
- [ ] 5.2 Run `openspec validate time-log-hhmm-format --strict` and verify it passes
