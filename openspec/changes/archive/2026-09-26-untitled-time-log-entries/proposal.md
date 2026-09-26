# Proposal

## Why

A time log entry written with only tags, such as `- #proj-01 #research` (common when continuing an earlier task), is dropped by the log parser because its activity text is empty once tags are removed. The day report then lists a `*GAP of N min*` where the entry was, and the entry's time and tags are left out of every total, by-tag sum, and period summary. The entry is real logged time, not a gap.

## What Changes

- The time log parser records an entry whose activity line has only tags, or no text at all, as long as it has tags or a `start:`/`end:` line. A stray empty `-` with neither is still ignored.
- As a result, the entry appears in the day log listing like any other (its line as written, times, duration, tags), no gap is listed in its place, and its time and tags count toward all totals and summaries.
- No report formatting or JSON changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `time-log`: entries with tags but no activity text, or with times but no text, are recorded rather than ignored.
- `time-report`: the day log listing gains a scenario for a tag-only entry (listed as written, no gap). The requirement text is unchanged.

## Impact

- `scripts/time_tracking.py`: `_create_time_log_entry` (drop condition).
- `test/unit/test_time_tracking.py`, `test/unit/test_time_report.py`.
- Totals in existing notes that contain tag-only entries will go up, and their spurious gaps and missing time will go down. That is the fix, not a regression.
- PATCH version bump on archive.
