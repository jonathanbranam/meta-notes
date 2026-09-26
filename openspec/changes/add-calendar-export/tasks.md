# Tasks

## 1. Dependencies and Python 3.11

- [x] 1.1 Add `requirements.txt` at the plugin root pinning exact current versions of `icalendar` and `recurring-ical-events`, and add the same pins to the Pipfile's `[packages]`; verify `pipenv install` succeeds and `pipenv run python -c "import icalendar, recurring_ical_events"` exits 0
- [x] 1.2 Raise `MIN_VERSION` in `scripts/meta_notes/__main__.py` to `(3, 11)`; verify with a `test_cli.py` test that runs `__main__.py` under a patched `sys.version_info` of 3.10 with `--json` and gets one JSON object with `ok` false naming 3.11 and 3.10 ("Python 3.10" scenario)
- [x] 1.3 Update "Python 3.10" to 3.11 in `README.md` and `doc/meta-notes.txt`, and replace "stdlib only" in `AGENTS.md` and `openspec/config.yaml` with the rule from the `cli` delta (standard library, except commands whose spec needs more, installed in the notes root's `.venv`); verify `grep -rn "3\.10" README.md doc/ AGENTS.md openspec/config.yaml` finds nothing

## 2. Config

- [x] 2.1 Add `scripts/meta_notes/config.py` with `load(root)` reading `.meta-notes` with `tomllib` and raising `ValueError` naming `.meta-notes` and the error's line on a parse error; verify with `test/unit/test_config.py` tests for "Existing sentinel" (the exact line `init` writes parses to `{}`), "Unknown key", and "Invalid TOML"
- [x] 2.2 Verify "Other commands unaffected": a `test_cli.py` test with `.meta-notes` containing `[calendar` runs `main(["tasks", "--json", ...])` and gets `ok` true
- [x] 2.3 Document `.meta-notes` config in `doc/meta-notes.txt` under a `*meta-notes-config*` tag (TOML, tables per command, unknown keys ignored, parse errors, the `[calendar]` example from design.md); verify `:helptags doc` reports no errors

## 3. Shim

- [x] 3.1 Rewrite `bin/meta-notes` per design.md decision 2: keep symlink resolution; `exec python3` when the first non-option argument is `init`; otherwise find the root from `--root DIR`/`--root=DIR` anywhere in argv, then `META_NOTES_ROOT`, then an upward walk from `$PWD` for a `.meta-notes` file that stops after `$HOME`; `exec "$root/.venv/bin/python3"` when `-x`, else `python3`; verify `bash -n bin/meta-notes` passes
- [x] 3.2 Add `test/unit/test_shim.py` running `bin/meta-notes` by subprocess in a `tmp_path` notes root whose `.venv/bin/python3` is a stub script that writes a marker file and exits; verify tests for "Virtualenv present" (run from a subdirectory), "Root passed after the subcommand" (`--root` and `--root=` forms, cwd outside the root), `META_NOTES_ROOT`, "Broken virtualenv" (dangling link falls back; assert the marker is absent), "Init ignores the virtualenv", and no `.venv` falls back to `python3`, with `HOME` set to `tmp_path`
- [x] 3.3 Document the shim's interpreter choice in `doc/meta-notes.txt` near `*meta-notes-cli*` and in README's Command Line section; verify both mention `.venv/bin/python3` and the fallback

## 4. Init

- [x] 4.1 In `init.py`, create `.meta-notes-cache/`, `ics/`, and `calendar/` as folder items, and ship `templates/cache-README.md` (the text from design.md decision 10) copied to `.meta-notes-cache/README.md` like a template (created, exists, overwritten with `--force`); verify with `test_init.py` tests for "Init in an empty directory", "Force keeps exports", and an edited README kept without `--force` and restored with it
- [x] 4.2 Add virtualenv setup to `init.py` per the `init` delta: `--python PATH` (plumbed through `cli.py`), version check with `<python> -c`, `<python> -m venv --prompt meta-notes .venv`, `.venv/bin/python3 -m pip install -r <plugin>/requirements.txt`, exists-and-left-alone reporting, `--force` removal and rebuild, and warnings that name the failing command and its output; verify with `test_init.py` tests that stub `subprocess.run` for "First init", "Explicit interpreter", "Existing virtualenv left alone", "Force rebuild", "Python too old", missing interpreter, and "Install fails" (`.venv` kept, warning says `init --force`)
- [x] 4.3 Add `.gitignore` handling to `init.py`: recognize `.venv`, `.venv/`, `/.venv`, `/.venv/` (and the same for `.meta-notes-cache`) ignoring surrounding whitespace, append missing lines (adding a newline first when the file doesn't end with one), report each as an item, and warn when there's no `.gitignore`; verify with tests for "Entries appended", "Existing entry recognized", "Re-run adds nothing", "No .gitignore", and a file without a trailing newline
- [x] 4.4 Add report items and messages for the new kinds (`cache-readme`, `venv`, `gitignore`) to `cmd_init`'s text output and to `s:init_messages` in `autoload/meta_notes/notes.vim`; in `test/init.vader` and the existing `test_init.py`/`test_cli.py` init tests, pre-create `.venv/` (or pass `--python` to a missing path) so no test builds a real virtualenv; verify the "JSON report" test and `./run_tests.sh test/init.vader` pass
- [x] 4.5 Document init's new work in `doc/meta-notes.txt` (`--python`, `.venv`, `--force` rebuild, the cache folders and README, `.gitignore`, the calendar-unavailable warning) and README's Command Line section; verify both mention `--python` and `.meta-notes-cache/`

## 5. Calendar: reading exports

- [x] 5.1 Add a test helper in `test/unit/test_calendar.py` that writes `.ics` text (VTIMEZONE, events, recurring series, overrides, attendees) and builds Google-style zips of several calendars at test time, setting file mtimes explicitly; verify with a smoke test that a built zip lists its members with `zipfile`
- [x] 5.2 Add `scripts/meta_notes/calendar.py` with settings from `config.load` (`email`, `timezone` via `zoneinfo`, `stale_days`, `calendars`) and export discovery (`--ics`, else newest `*.ics`/`*.zip` directly in `ics/` by mtime); import `icalendar` and `recurring_ical_events` inside the command so an `ImportError` becomes the not-installed error; verify with tests for "Newest export wins", "Explicit path", "Other files ignored", an unknown timezone error, and "No virtualenv" (import patched to fail; `tasks` still works)
- [x] 5.3 Read calendars from a `.ics` or `.zip` (members read in memory, named by `X-WR-CALNAME` or file stem, `calendars` matched case-insensitively); verify with tests for "Selected calendar", "Unknown calendar name", "All calendars", and `calendars` ignored for a plain `.ics`

## 6. Calendar: agenda

- [x] 6.1 Expand events for the period with `recurring_ical_events` per calendar, convert to the display timezone, keep only events overlapping the period's days (the stray-date safety filter), drop cancelled and declined events, place all-day events on each covered day, and sort all-day first then by start; verify with tests for "Timezone conversion", "Declined meeting hidden", "Email unset", "Moved occurrence", "Series split at an edit", "Occurrence recorded twice", "Multi-day all-day event", a cancelled override, and a single `ATTENDEE` value (not a list)
- [x] 6.2 Build the text lines and JSON dict per the `calendar-agenda` "Agenda output" requirement, including the calendar suffix when more than one calendar is loaded and `source` fields; verify with tests for "Text output", "Empty day", "Default period", "Week range", and the JSON shape
- [x] 6.3 Add the stale warning (`stale_days`, default 3, age from mtime); verify with tests for "Default threshold" and "Configured threshold" using a fixed `today`

## 7. Calendar: cache and pruning

- [x] 7.1 Build the cache per design.md decision 7: key from file name, size, mtime ns, and sorted loaded calendar names; write `<key>.ics` (kept VTIMEZONEs and calendar properties; one-off events and `UNTIL` series ending before the 30-day horizon dropped; old overrides dropped; deduplicated by `(UID, RECURRENCE-ID)` keeping the highest `(SEQUENCE, LAST-MODIFIED)`) and `<key>.json`; create `calendar/` if missing; verify with tests for "Reuse", "New export", "Calendar selection changed", that agendas from cache and export are equal for a range within the horizon, and that the cached file is smaller than a source with old history
- [x] 7.2 Handle ranges before the horizon (read the export when present, else cache plus warning) and the missing-export fallback (newest entry by recorded mtime, missing-export warning, stale check from the recorded mtime); verify with tests for "Export deleted after caching", "Nothing at all" (error names the absolute `ics/` path), and a range 60 days back with and without the export
- [x] 7.3 Prune per the `calendar-agenda` "Pruning" requirement and report deleted paths in `pruned` and on stderr; verify with tests for "Old exports removed", "Other files kept", entries for an old `calendars` setting removed, the `--ics` entry kept for its run, and the no-exports case keeping only the newest entry
- [x] 7.4 Add `meta-notes cache clear`; verify with tests for "Clear" and "Nothing to clear", and that it runs with the calendar libraries' import patched to fail

## 8. CLI wiring and docs

- [x] 8.1 Add `calendar [--date PERIOD] [--ics PATH]` and `cache clear` subcommands and `cmd_calendar`/`cmd_cache_clear` in `cli.py`, mapping `ValueError` to `CliError`, with warnings and `pruned` on stderr without `--json`; verify with `test_cli.py` tests through `main([...])` for a text agenda, `--json` success, and the no-export error with `--json` (one JSON object, nothing on stderr)
- [x] 8.2 Document `meta-notes calendar` and `meta-notes cache clear` in `doc/meta-notes.txt` under `*meta-notes-cli-calendar*` (exporting from Google Calendar into `ics/`, zip calendars, settings, output, staleness, cache, pruning, errors), add examples and the command list entry to README, and add `calendar.py`, `config.py`, `test_calendar.py`, `test_config.py`, `test_shim.py`, and `requirements.txt` to README's project structure tree; verify `:helptags doc` reports no errors and each file appears in the tree

## 9. Planning skills

- [x] 9.1 Update `skills/daily-plan/SKILL.md` and `skills/weekly-plan/SKILL.md` to gather meetings with `meta-notes calendar --date <day or MON..FRI> --json`, report the export's age and warnings, and on failure offer exporting into the named `ics/` folder or a screenshot (and `meta-notes init` when calendar support isn't installed); update `weekly-plan`'s description to drop "from a calendar screenshot"; verify by reading both skills against the `ceremony-skills` delta's scenarios
- [x] 9.2 Update `docs/planning-system.md` (calendar input for daily and weekly planning) and the `weekly-plan` line in `doc/meta-notes.txt`; verify `grep -rn screenshot skills/ doc/ docs/planning-system.md` shows only the fallback wording

## 11. Attendance

- [x] 11.1 In `calendar.py`, add per-event `mine`, `organizer`, `response`, `attendee_count`, and `attendees` (people only, first 20) per the `calendar-agenda` "Attendance" requirement; verify with tests for "Maybe", "No reply", "Created by the user", "Personal event without attendees", "Large meeting", a single `ATTENDEE` value, and `email` unset (response null, mine false)
- [x] 11.2 Change the text output to drop locations and add ` [maybe]`/` [no-reply]` (not for `mine` events); update "Text output" and other text tests; verify `pipenv run pytest test/unit/test_calendar.py`
- [x] 11.3 Update `doc/meta-notes.txt` (`*meta-notes-cli-calendar*` output and JSON fields) and README if it shows agenda text; verify `:helptags doc` reports no errors

## 10. Integration

- [ ] 10.1 In a scratch notes root with a `.gitignore`, run `meta-notes init` and confirm `.venv`, the cache folders and README, and the `.gitignore` lines; save a real Google export zip into `.meta-notes-cache/ics/`, set `[calendar]` in `.meta-notes`, run `meta-notes calendar --date <next MON..FRI>` twice (the second from cache) with and without `--json`, compare against Google Calendar, add six more exports to check pruning, and run `meta-notes cache clear`; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
