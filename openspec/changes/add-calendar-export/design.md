## Context

See proposal.md for motivation. The prototype notes in
`docs/Add calendar export to meta-notes.md` cover the export format, the
libraries, and the pitfalls; this design doesn't repeat them.

Current state that shapes the approach:

- `bin/meta-notes` is a bash shim that runs `python3
  scripts/meta_notes/__main__.py`. It knows nothing about notes roots;
  root resolution (`--root`, `META_NOTES_ROOT`, upward `.meta-notes`
  search bounded by `$HOME`) lives in `cli.resolve_root` and
  `root.find_root`.
- The CLI is stdlib-only and checks for Python 3.10 in `__main__.py`.
  `python3` here is a pyenv shim, so which interpreter it is depends on
  the directory and environment.
- Vim calls the shim with `--root <cwd> --json` after the subcommand
  (`autoload/meta_notes/cli.vim`). Skills call `meta-notes` by name from
  inside the notes root.
- `.meta-notes` holds a single comment line, written by `init`.
- A real export is a Google zip of one `.ics` per calendar, the main one
  about 38 MB and ~10,000 `VEVENT`s, mostly history.

## Goals / Non-Goals

**Goals:**
- One place decides which interpreter runs: the shim.
- Only the calendar code imports third-party libraries; every other
  command still works on the plain `python3` if the virtualenv is broken
  or missing.
- A new export needs no steps beyond saving it into `ics/`.
- Parse each export once.

**Non-Goals:**
- Detecting that `requirements.txt` changed and reinstalling. `init
  --force` rebuilds; anything smarter waits for `uv`.
- Keeping the bash root search identical to `find_root` in every edge
  case. It only picks an interpreter; Python still resolves the root.

## Decisions

### 1. A virtualenv per notes root, built by `init`

`<root>/.venv/` is created with `<python> -m venv --prompt meta-notes
.venv`, where `<python>` is `--python PATH` or `python3` from `PATH`, then
`.venv/bin/python3 -m pip install -r <plugin>/requirements.txt`.

- Exists, no `--force`: nothing is done. The report item says `.venv`
  exists and was left alone, and that `--force` rebuilds it. This holds
  with `--python` too.
- `--force`: `rm -rf .venv`, then build.
- Before building, `init` runs `<python> -c` to check the version is at
  least 3.11. Missing interpreter, too old, venv failure, or pip failure:
  `init` still succeeds, with a warning that calendar support isn't
  available and the command that failed. A failed pip leaves `.venv` in
  place (the shim can still use it for everything else); the warning says
  to run `init --force` once fixed.
- `requirements.txt` pins exact versions.

Alternatives: `uv run --script` (sandboxed Claude sessions have trouble
with uv; `.venv/bin/python3` always works), vendoring the libraries into
`scripts/` (third-party code in the repo, LGPL, manual updates), lazy
import with install instructions (installs into whatever pyenv resolves),
and a virtualenv in the plugin directory (the user chose the notes root,
next to the data and ignored by its `.gitignore`).

### 2. The shim picks the interpreter

```
 bin/meta-notes
   ├─ first non-option argument is `init`  ─▶ exec python3
   ├─ root = --root VALUE | --root=VALUE  (anywhere in argv)
   │         | $META_NOTES_ROOT
   │         | walk up from $PWD for a .meta-notes file, stop after $HOME
   ├─ [ -x "$root/.venv/bin/python3" ]  ─▶ exec it
   └─ otherwise                         ─▶ exec python3
```

`init` always uses `python3`: it has its own root rules (target
directory, ignores `META_NOTES_ROOT`), and `--force` deletes the
virtualenv it would otherwise be running from.

The bash walk only checks for the file; it doesn't copy `find_root`'s
permission checks. A difference can only choose the wrong interpreter,
never the wrong root. A virtualenv whose base Python was removed has a
dangling `python3` link, which fails `-x`, so the shim falls back.

Alternative: pick the interpreter in `__main__.py` and re-exec. That
starts Python twice on every call and needs the root resolved before
argument parsing. The user preferred to handle it once in the shim.

### 3. Imports and failure

Only `scripts/meta_notes/calendar.py` imports `icalendar` and
`recurring_ical_events`, and only when the `calendar` command runs. An
`ImportError` becomes a normal CLI error: calendar support isn't
installed in this notes root; run `meta-notes init` (or `init --force`,
when `.venv` exists). `cache clear` imports nothing third-party.

`__main__.py`'s minimum becomes 3.11.

### 4. Config: `.meta-notes` as TOML

`config.load(root)` reads `.meta-notes` with `tomllib` and returns a dict.
Only commands that need config call it, so a TOML error can't break
unrelated commands. A parse error fails the calling command with the file
and tomllib's message.

```toml
# meta-notes notes root. Created by `meta-notes init`; keep and commit it.

[calendar]
email = "me@example.com"        # whose declines to hide; unset: none hidden, warning
timezone = "America/New_York"   # display timezone; unset: system local
stale_days = 3                  # unset: 3
calendars = ["me@example.com"]  # zip members to load; unset: all
```

Unknown keys are ignored. `init` doesn't write a `[calendar]` table; the
docs show one.

### 5. Finding the export

`--ics PATH` wins, and may be `.ics` or `.zip`. Otherwise the newest
`*.ics` or `*.zip` directly in `.meta-notes-cache/ics/`, by modification
time. The export's age for staleness is its modification time, which for
a download is when it was saved.

### 6. Zip calendars

A zip's calendars are its `*.ics` members, read with `zipfile` without
extracting. A calendar's name is its `X-WR-CALNAME`, falling back to the
member's filename stem. `calendars` in config matches either,
case-insensitively. A configured name that matches nothing is an error
that lists the available names. With `calendars` unset, all are loaded.
The JSON output lists available and loaded names either way, so a skill
can suggest the setting. A plain `.ics` is one calendar, and `calendars`
doesn't apply to it.

### 7. The cache

```
 .meta-notes-cache/
 ├── README.md                    what each folder is for (from init)
 ├── ics/                         exports, kept to the newest 5
 └── calendar/
     ├── <key>.ics                pruned, deduped VCALENDARs
     └── <key>.json               source name, size, mtime, loaded and
                                  available calendars, horizon, built
```

`key` is a short SHA-256 of the export's file name, size, modification
time (ns), and the sorted loaded calendar names, so changing `calendars`
builds a new entry. The lookup order:

```
 export found?
   ├─ yes ─ <key>.ics exists? ─ yes ─▶ load it
   │                          └ no ──▶ parse export, prune, dedupe,
   │                                   write <key>.ics + .json, load it
   └─ no ── any <key>.json? ─ yes ─▶ load newest (by recorded source
                            │        mtime); warn: export missing
                            └ no ──▶ error naming <root>/.meta-notes-cache/ics/
```

Building the cache:
- Keep every `VTIMEZONE` and calendar-level property.
- Drop a one-off event (no `RRULE`/`RDATE`) that ends before the horizon,
  30 days before the build date.
- Drop a series whose `RRULE` has an `UNTIL` before the horizon. Keep
  `COUNT` series and series without an end; working out where they end
  needs expansion.
- Drop a `RECURRENCE-ID` override when both its `RECURRENCE-ID` and its
  `DTSTART` fall before the horizon.
- Deduplicate by `(UID, RECURRENCE-ID)`, keeping the highest
  `(SEQUENCE, LAST-MODIFIED)`. This settles the prototype's open question
  whether the library dedupes: we do it here, once.

The cache is text, so it can be opened and inspected. A requested range
that starts before the horizon is read from the export itself, without
the cache, when the export exists; otherwise from the cache, with a
warning that earlier events were pruned.

Alternative: pickle the parsed `Calendar`. It's faster to load, but opaque
and tied to library versions.

### 8. Pruning exports and cache entries

Every `calendar` call prunes both `ics/` and `calendar/`, after choosing
its source, so neither folder grows:

- `ics/`: exports beyond the newest 5 by modification time are deleted.
- `calendar/`: an entry is kept only when its recorded source is one of
  the kept exports and its loaded calendars match the current
  `calendars` setting. Everything else goes, including entries built for
  an older `calendars` setting and for a `--ics` file outside `ics/`.
- With no exports in `ics/`, every entry except the newest is deleted,
  and the newest is kept for the missing-export fallback.

A `--ics` call prunes `ics/` the same way, but keeps its own entry. Deleted
files are listed in the JSON output (`pruned`) and, without `--json`,
reported on stderr.

### 9. Building the agenda

- `recurring_ical_events.of(cal).between(start, end + 1 day)` per loaded
  calendar.
- Then, as the prototype found `.between()` can return an event outside
  the range: convert `DTSTART`/`DTEND` to the display timezone and keep
  only events that overlap the requested days. Normalize all-day `date`
  values to the display timezone's midnight before sorting.
- Leave out `STATUS:CANCELLED`, and events where the attendee whose
  address matches `email` (case-insensitive, `mailto:` stripped) has
  `PARTSTAT=DECLINED`. `ATTENDEE` may be one value or a list.
- An all-day event spanning several days appears on each day in range. A
  timed event appears on its start day.

Text output, one heading per day in the range, including empty days:

```
## 2026-09-28 Mon
all day  Company holiday
09:00-09:30  Standup [yes]
10:00-11:00  Vendor demo [maybe]
13:00-14:00  Design review [mine]
15:00-16:00  Focus
```

The text shows only the user's own attendance: `[mine]` for events they
organized (or personal events with no organizer or attendees in the
calendar named by `email`), otherwise `[yes]`, `[maybe]`, or
`[no-reply]` from their `PARTSTAT`. Locations and other attendees are
JSON only, to keep the text short. With more than one calendar loaded,
each line ends with `(<calendar>)`.

The JSON object has `days` (each with `date` and `events`: `start`,
`end`, `all_day`, `title`, `location`, `calendar`, `mine`, `organizer`,
`response`, `attendee_count`, and `attendees`, capped at 20; rooms and
resources, `CUTYPE` `ROOM` or `RESOURCE`, aren't counted), `source` (path,
`exported` time, `age_days`, `cached`, `available` and `loaded`
calendars), `pruned`, and `warnings`.

### 10. The cache folder and `meta-notes cache clear`

`init` creates `.meta-notes-cache/`, `ics/`, and `calendar/`, each
reported as a folder item, and writes `.meta-notes-cache/README.md` from a
file shipped in the plugin, reported like a template: created when
missing, left alone when present, overwritten with `--force`. The README
is a few lines:

```markdown
# meta-notes cache

Created by `meta-notes init`. Not committed (see .gitignore).

- `ics/` - Google Calendar exports (.zip or .ics). Save new exports here;
  `meta-notes calendar` reads the newest and keeps the latest 5.
- `calendar/` - parsed calendars built from the exports. Safe to delete;
  `meta-notes cache clear` empties it.
```

`meta-notes cache clear` deletes the files in `calendar/` and reports how
many it removed. It never touches `ics/` or the README. A missing
`calendar/` is not an error. `calendar` creates `calendar/` if it's
missing, so a root set up before this change, or a deleted folder, still
works.

### 11. Skills

`daily-plan` and `weekly-plan` run `meta-notes calendar --date <range>
--json` for the day or workweek they plan:
- `ok`: use the agenda, and say how old the export is and any warnings
  (stale, export missing).
- error: tell the user to export from Google Calendar (Settings, Import &
  export, Export) into the `ics/` path from the error, or to provide a
  screenshot, and continue with whichever they choose.

### 12. Tests

`icalendar` and `recurring-ical-events` go in the Pipfile at the
`requirements.txt` pins, so `pipenv run pytest` covers the calendar code.
Test calendars are written as `.ics` text in the tests and zipped at test
time. Shim tests run `bin/meta-notes` in a temporary root whose
`.venv/bin/python3` is a stub script that records it was called. Init
tests stub the interpreter and pip calls rather than building a real
virtualenv.

## Risks / Trade-offs

- [The first parse of a 38 MB export takes seconds] → It happens once
  per export; later calls load the pruned cache.
- [Pruning by `UNTIL` keeps `COUNT` and endless series, so the cache
  isn't minimal] → They're a small share of the file; one-off history
  makes up most of it.
- [The bash root search differs from `find_root` in edge cases] → It only
  chooses the interpreter; the wrong choice falls back to `python3`, and
  commands other than `calendar` work on either.
- [Removing pyenv's base Python breaks `.venv`] → The shim falls back;
  `calendar` reports that it isn't installed; `init --force` rebuilds.
- [Deleting exports automatically loses data] → Only files in `ics/`,
  which are downloads that can be exported again; the newest 5 are kept
  and deletions are reported.
- [Exports and cache hold work calendar data inside the notes repo] →
  `init` adds both to `.gitignore`, or warns when there isn't one.
- [Python 3.11 breaks 3.10 users] → The version check reports it clearly;
  3.10 is end of life next month.

## Migration Plan

1. Set the `python3` on `PATH` to 3.11 or newer (for example `pyenv
   global 3.11.6`).
2. In each notes root, run `meta-notes init` once. Existing folders,
   templates, skills, and the sentinel are untouched; it creates `.venv`,
   the cache folders and README, and the `.gitignore` entries.
3. Add a `[calendar]` table to `.meta-notes` and commit it.
4. Save the Google export zip into `.meta-notes-cache/ics/`.

Rollback: delete `.venv/`; the shim goes back to `python3`, and only
`calendar` stops working.
