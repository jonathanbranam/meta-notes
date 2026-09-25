## 1. Prerequisites

- [ ] 1.1 Confirm `find-tasks-enhancements` is archived and that `scripts/period.py` (`parse_period`) and `scripts/tags.py` (`canonical_tag`) exist on main; verify `pipenv run pytest test/unit/test_period.py test/unit/test_tags.py` passes

## 2. Day calculations in `time_tracking.py`

- [ ] 2.1 Add `GAP_THRESHOLD_MINUTES = 2`, `MISSING_THRESHOLD_MINUTES = 10`, and `entry_gap_minutes(prev, nxt)` (signed whole minutes, `None` when a time is missing); add tests in `test/unit/test_time_tracking.py` for gap, overlap, zero, and missing times; verify they pass
- [ ] 2.2 Add `day_log_items(entries)` returning entries in file order with gap/overlap items (gap only when > 2 min; overlap for any negative gap; `start`/`end` = earlier end, later start); test the 10-min gap, 2-min ignored, 9-min overlap, and missing-end chain-break scenarios from the spec; verify they pass
- [ ] 2.3 Add `day_totals(entries)` (`work_minutes` via `analyze_work_day`, `total_minutes`, `earliest`/`latest` over all present times, `span_minutes`, `missing_minutes` only above 10); test the 07:08–17:51 / 9 hr 6 min → 1 hr 37 min scenario, the under-threshold case, and personal-at-edges (2 hr work, 4 hr total); verify they pass
- [ ] 2.4 Add `tag_totals(entries)` (canonical names without `#`, each tag once per entry) and `HIGHLIGHTED_TAGS` with `highlighted_totals(entries)` (group names via `calculate_time_by_group`, other names as tags, zeros dropped, list order kept); test the `#mtg` + `#meeting` merge, the group counting an entry once, and the highlighted order/filtering scenario; verify they pass

## 3. Report building and text in `time_report.py`

- [ ] 3.1 Replace `_get_week_analyses` with `_load_days(root, start, end)` returning `(date, entries | None)` for every day; add `test/unit/test_time_report.py` with a `tmp_path` notes root covering a present note, a missing note, and a Mon–Sun span; verify it passes
- [ ] 3.2 Add `build_period_report(root, start, end)` and `format_period_report(data)` producing `Summary for <START> to <END>` with Total Time (work, total, highlighted), Time per tag (alphabetical), and Day Summaries (`(no log)` for empty days); test the weekend-entry, no-log day, and month (30 items) scenarios; verify they pass
- [ ] 3.3 Add `build_day_report(root, day, path)` and `format_day_report(data)` with the day log listing (activity line, `start`, `end`, `time`, `tags`, `*MISSING START TIME*` / `*MISSING END TIME*`, `*GAP of N min*`, `*Overlap of N min*`), the day Total Time with `*missing time*`, the unchanged Time by Tag / Work vs Non-Work / Plan Adherence sections, and the Mon–Sun week summary, in that order; keep `generate_report(filepath)` as a wrapper; test section order, the no-log note, and the entry formatting scenarios; verify they pass
- [ ] 3.4 Remove `format_week_summary` and the Mon–Fri loop, and rewrite or drop their tests in `test_time_tracking.py`; verify `pipenv run pytest test/unit/` passes
- [ ] 3.5 Make `file` optional and add `--date` to `time_report.py`: both is an error, neither means today, invalid periods print the `date-period` error, a single-day `--date` with no note fails with `Daily note not found: <path>`, a longer period prints the period report, and `--date` uses the current directory as the notes root; test with `subprocess` or `main()` in `test_time_report.py` covering date, file, default, missing note, both-given, and invalid date; verify they pass

## 4. CLI `meta-notes time`

- [ ] 4.1 Add `scripts/meta_notes/time.py` with `run(root, date_text, today=None) -> (lines, data)` building the day or period report and the JSON shape from design.md (items with `kind`, `line`, `minutes`, null times; `report` text); add `cmd_time` and a `time` subparser (`--date`, common options, resolves root) in `cli.py` that turns `ValueError` into `CliError`
- [ ] 4.2 Add tests in `test/unit/test_cli.py` for: running from a subfolder, the JSON entry fields, a gap item, null missing times, `report` equal to the text output, the invalid `--date --json` error object, and read-only (no files changed in the root); verify `pipenv run pytest test/unit/test_cli.py` passes

## 5. Vim

- [ ] 5.1 Change `meta_notes#time_tracking#ShowReport` to take the date from the note's filename, call `meta_notes#cli#Run(['time', '--date', l:date])`, show `l:result.report` in the `Time Report` buffer, and report failures with `echohl ErrorMsg` instead of `echoerr`, keeping the daily-note check
- [ ] 5.2 Add `test/time_report.vader` (temp-dir pattern from AGENTS.md, with `.meta-notes` and a daily note) covering the report buffer contents from a daily note, the error outside a daily note, and a CLI failure that raises no exception; verify `./run_tests.sh test/time_report.vader` passes

## 6. Docs and release

- [ ] 6.1 Update `doc/meta-notes.txt` (`:MetaNotesTimeReport`, a `meta-notes time` entry under the CLI section, and the new report sections, including the Mon–Sun week summary replacing `hours worked` / `Weekly total worked`) and the README command-line examples; verify `:helptags doc` reports no errors and the new tags resolve
- [ ] 6.2 Run the full suites, `pipenv run pytest test/unit/` and `./run_tests.sh`, and verify both pass; run `meta-notes time --date <this week>` against a real notes root and check the output against the work copy's `time_log.py` for the same week
- [ ] 6.3 When archiving, bump the MINOR version in `scripts/meta_notes/__init__.py`, tag `v<version>`, and push the tag; verify `meta-notes --version` shows the new version
