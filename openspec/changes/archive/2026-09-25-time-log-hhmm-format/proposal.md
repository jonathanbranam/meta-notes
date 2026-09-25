## Why

Bare `HH:MM` is now the preferred way to write time log timestamps. A daily note's filename already encodes the date, so repeating it in every `start:` / `end:` line is redundant. The parser already supports bare times (24-hour `09:10` and 12-hour `3:20pm`, with the date taken from the filename), but the rest of the system has not caught up:

- The daily template still pre-fills every entry with the full date (`* start: {{date}} HH:MM`, which renders as `* start: 2026-09-25 Fri HH:MM`), so the redundant form is the default and has to be deleted by hand.
- The full-date form requires the day abbreviation. A hand-typed `2026-09-25 08:00` fails to parse and the entry is silently dropped from reports.
- Syntax highlighting only matches `HH:MM am/pm`, so 24-hour times are not highlighted.
- The documentation does not describe the time log entry format at all, and docstrings still present `YYYY-MM-DD DDD HH:MM` as the primary form.
- No spec records which timestamp formats are accepted.

## What Changes

- `templates/daily.md`: the time log placeholder becomes `* start: HH:MM` / `* end:   HH:MM`.
- Full-date timestamps accept `YYYY-MM-DD HH:MM` in addition to `YYYY-MM-DD DDD HH:MM` (the day abbreviation becomes optional), so hand-typed full dates without a day abbreviation are parsed instead of dropped.
- `after/syntax/markdown.vim`: `metaNotesTime` also highlights 24-hour `HH:MM` times in `start:` / `end:` lines.
- `doc/meta-notes.txt`: the time tracking section documents the log entry structure and the accepted timestamp formats, with bare `HH:MM` shown first.
- Docstrings in `scripts/time_tracking.py` (`_parse_time_log_lines`, `_parse_entry_time`, `_parse_datetime`) lead with bare `HH:MM`.
- New tests cover `YYYY-MM-DD HH:MM` and a single log that mixes formats.

Already implemented and out of scope, except for being recorded in the spec:

- Bare 24-hour `HH:MM` and 12-hour `H:MMam/pm` resolved against the date in the daily note's filename (`_parse_bare_time_24h`, `_parse_time`, `_parse_entry_time`, `_extract_date_from_filepath`).
- Each `start:` / `end:` value is parsed independently, so formats may be mixed within a file.

## Capabilities

### New Capabilities

- `time-log`: Structure of daily note time log entries (`### Log` section, activity line with tags, `start:` / `end:` / note detail lines) and the accepted timestamp formats: bare `HH:MM`, bare `H:MMam/pm`, `YYYY-MM-DD HH:MM`, and `YYYY-MM-DD DDD HH:MM`. Bare times take their date from the note's filename; a bare time in a file without a date in its name is unparseable. An unparseable timestamp leaves that field unset.

### Modified Capabilities

*(none — no existing spec covers time tracking)*

## Impact

- `scripts/time_tracking.py`: `_parse_datetime` regex; docstrings.
- `test/unit/test_time_tracking.py`: tests for `YYYY-MM-DD HH:MM` and mixed formats.
- `templates/daily.md`: time log placeholder. Test fixtures that copy or render it change with it: `test/fixtures/init_templates/daily.md` and the `test/fixtures/templates/daily-*.md` goldens from the `note-create` change.
- `after/syntax/markdown.vim`: 24-hour time highlighting.
- `doc/meta-notes.txt`: time log format documentation.
- `test/syntax_test.md`: sample log uses bare `HH:MM`.
- Existing notes need no migration: every format that parses today still parses.
