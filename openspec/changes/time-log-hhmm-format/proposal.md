## Why

Writing `* start: 2026-06-14 08:00` is redundant inside a daily note whose filename already encodes the date. Allowing bare `HH:MM` timestamps (and dropping the required day-of-week abbreviation from full-date timestamps) makes time log entries faster to write and easier to read.

## What Changes

- The `_parse_datetime` function is extended to accept `YYYY-MM-DD HH:MM` in addition to the existing `YYYY-MM-DD DDD HH:MM` (day abbreviation is now optional).
- When a bare `HH:MM` value appears as a `start:` or `end:` field, the date is inferred from the daily note's filename (already handled by `_extract_date_from_filepath`, already wired into `_parse_entry_time` — this path just needs to be validated and tested).
- Daily note time log entries may now mix both formats in the same file; each entry is resolved independently.

## Capabilities

### New Capabilities

- `time-log-flexible-timestamps`: Parsing rules for `start:` / `end:` fields that accept `YYYY-MM-DD HH:MM` (no day abbreviation) and bare `HH:MM` (date inferred from filename), in addition to the existing `YYYY-MM-DD DDD HH:MM` format.

### Modified Capabilities

*(none — no existing spec files)*

## Impact

- `scripts/time_tracking.py`: `_parse_datetime` regex, `_parse_entry_time` call chain, docstrings.
- `test/unit/test_time_tracking.py`: new test cases for both new formats.
- No changes to vim plugin code, report scripts, or note file formats.
