## Why

`daily-plan` and `weekly-plan` get meetings from a calendar screenshot. It's
slow, easy to misread (cut-off columns, missing day headers, which week is
shown), and can't be automated. Google Calendar has no API access here, but
it exports every calendar as a zip of `.ics` files. Parsing the latest
export into a plain-text agenda lets the skills read the calendar directly.

A prototype against a real 38 MB, multi-year export
(`docs/Add calendar export to meta-notes.md`) showed that hand-rolled RRULE
expansion gets the iCalendar spec wrong in ways that duplicate or drop
meetings. `icalendar` and `recurring-ical-events` handle every pattern in
that export. They're third-party, so this change also gives the plugin a
way to install and run Python dependencies: a virtualenv per notes root,
created by `init` and used by the `bin/meta-notes` shim.

## What Changes

- **Python 3.11 minimum** (was 3.10), for stdlib `tomllib`. **BREAKING**
  for anyone on 3.10; 3.10 reaches end of life in October 2026.
- **Notes root virtualenv.** The plugin ships `requirements.txt` (pinned
  `icalendar`, `recurring-ical-events`). `meta-notes init`:
  - when `.venv/` doesn't exist, runs `python3 -m venv --prompt meta-notes
    .venv` with the `python3` on `PATH`, or with the interpreter given by
    a new `--python PATH` option, then `.venv/bin/python3 -m pip install
    -r <plugin>/requirements.txt`
  - when `.venv/` exists, leaves it alone and reports that, and why, even
    if `--python` is given
  - with `--force`, removes `.venv/` and builds it again
  - when the interpreter is missing or older than 3.11, or venv or pip
    fails, still succeeds and warns that calendar support isn't available
  - creates `.meta-notes-cache/` with `ics/` and `calendar/`, and a short
    `.meta-notes-cache/README.md` saying what each folder is for
  - appends `.venv/` and `.meta-notes-cache/` to the root's `.gitignore`
    when they aren't already ignored there; with no `.gitignore`, warns
    the user to ignore them
- **Shim uses the virtualenv.** `bin/meta-notes` finds the notes root
  (`--root`, `META_NOTES_ROOT`, or the upward `.meta-notes` search) and
  runs `<root>/.venv/bin/python3` when it's executable, otherwise
  `python3`. `init` always runs on `python3`.
- **Config in `.meta-notes`.** The sentinel is read as TOML with `tomllib`.
  Existing sentinels (a single comment line) are valid, empty config. A
  `[calendar]` table holds `email`, `timezone`, `stale_days`, and
  `calendars`.
- **`meta-notes calendar [--date PERIOD] [--ics PATH] [--json]`** prints a
  day-by-day agenda for PERIOD (default today), using the shared `--date`
  syntax:
  - source: `--ics PATH`, otherwise the newest `.ics` or `.zip` in
    `.meta-notes-cache/ics/`, by modification time
  - a Google export zip is read directly; `calendars` in config selects
    which calendars in it to load, and all are loaded when unset
  - declined events (by the configured `email`) and cancelled events are
    left out; times shown in the configured `timezone`
  - each export is parsed once and cached in `.meta-notes-cache/calendar/`,
    keyed by the export's name, size, and modification time
  - keeps the 5 newest exports in `ics/` and deletes older ones; keeps
    cache entries only for the kept exports and the current `calendars`
    setting, deleting the rest
  - warns when the export is older than `stale_days` (default 3)
  - with no export but a cached calendar, uses the newest cached calendar
    and warns that its export is missing
  - with no export and no cache, fails with an error naming the folder to
    export into
- **`meta-notes cache clear`** deletes the contents of
  `.meta-notes-cache/calendar/`, and never the exports in `ics/` or the
  README.
- **Skills.** `daily-plan` and `weekly-plan` run `meta-notes calendar` for
  the days they plan. With an agenda, they use it and pass on its
  warnings. Without one, they ask the user to export into
  `.meta-notes-cache/ics/` (naming the full path) or to provide a
  screenshot, as today.

## Capabilities

### New Capabilities
- `calendar-agenda`: the `calendar` command: export discovery, zip
  calendars, filtering, output, staleness, the export cache, pruning, and
  `cache clear`
- `notes-config`: `.meta-notes` as TOML config

### Modified Capabilities
- `cli`: Python 3.11 minimum; the shim runs the notes root's virtualenv;
  third-party libraries allowed for commands that need them, from the
  virtualenv only
- `init`: virtualenv setup, `--python`, the cache folder, and `.gitignore`
  entries
- `ceremony-skills`: `daily-plan` and `weekly-plan` read meetings from
  `meta-notes calendar`, falling back to a screenshot

## Non-Goals

- Live calendar sync or Google API access. Exports stay manual.
- `uv`, or reinstalling dependencies on re-run without `--force`. If
  dependency handling needs more than this, a later change can move to
  `uv`.
- Writing to calendars, or turning meetings into time-log entries.

## Impact

- `bin/meta-notes`: root resolution and virtualenv selection in bash
- `scripts/meta_notes/`: new `calendar` and `config` modules; `init`,
  `cli`, and `__main__` (version check) changes
- `requirements.txt`: new; `Pipfile`: the same libraries for tests
- `skills/daily-plan/SKILL.md`, `skills/weekly-plan/SKILL.md`
- `test/unit/`: calendar tests from generated `.ics` and `.zip` data, init
  virtualenv and `.gitignore` tests, shim tests
- `doc/meta-notes.txt`, `README.md`, `AGENTS.md`, `openspec/config.yaml`:
  Python 3.11, the dependency exception, the new commands
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
