## Context

`scripts/time_report.py` builds its report as text straight from
`time_tracking.py` helpers: `calculate_total_time_by_tag`,
`calculate_work_vs_nonwork`, `calculate_plan_adherence`, and a Mon–Fri
`format_week_summary` fed by `_get_week_analyses`. It takes only a file
path, and it finds the notes root by looking for `plan/daily` in that
path. `:MetaNotesTimeReport` runs the script through
`meta_notes#template#ExecutePythonScript` and puts its stdout in a
`Time Report` buffer.

The CLI wraps standalone scripts the way `query.py` wraps `find_tasks.py`:
it calls functions in-process (`scripts/` is on `sys.path`) and returns text
lines plus JSON data in an `Output`. `note --render` also returns its text
as a JSON field (`content`), which Vim reads.

`find-tasks-enhancements` supplies `scripts/period.py` (`parse_period`) and
`scripts/tags.py` (`canonical_tag`, `TAG_ALIASES`). `Tag.__post_init__`
already canonicalizes through `tags.py`, so every `TimeLogEntry` tag is
canonical with a leading `#`.

See proposal.md for motivation and specs/time-report for the behavior.

## Goals / Non-Goals

**Goals:**
- Build each report once as data, and render text and JSON from that one
  structure so the two can't drift.
- A single period summary serves both the day report's week summary and the
  `--date` period report.
- Reuse the existing calculations (`analyze_work_day`,
  `calculate_time_by_group`, `calculate_duration`) rather than adding
  parallel ones.

**Non-Goals:**
- Changing the existing Time by Tag, Work vs Non-Work, and Plan Adherence
  sections or their `#tag` / `2h 30m` formatting.
- Changing `calculate_work_vs_nonwork`'s tag rules.
- Configuring the highlighted tags or thresholds.

## Decisions

### Data first, text second

`time_report.py` gains `build_day_report(root, day, path) -> dict` and
`build_period_report(root, start, end) -> dict`, plus `format_day_report`
and `format_period_report`, which turn those dicts into lines.
`generate_report(filepath)` stays as a thin wrapper
(`format_day_report(build_day_report(...))`), so existing callers and tests
keep working. The dicts use the JSON shape directly: `HH:MM` strings,
`YYYY-MM-DD` dates, integer minutes, canonical tag names without `#`. The
formatters read only from the dicts.

*Alternative:* formatting from `TimeLogEntry` objects and serializing
separately for JSON. That gives two paths that could disagree. It would also
mean the `report` field and the JSON data came from different code.

### Calculations live in `time_tracking.py`

New pure functions over a day's entries:

- `entry_gap_minutes(prev, nxt) -> int | None`: `nxt.start - prev.end` in
  whole minutes, or `None` when either time is missing. Positive means a
  gap, negative means an overlap. It is the one calculation both come from.
- `day_log_items(entries) -> list[dict]`: entries in file order, with
  `{"kind": "gap"|"overlap", "minutes", "start", "end"}` items between
  them when the gap is `> GAP_THRESHOLD_MINUTES` (2) or `< 0`.
- `day_totals(entries) -> dict`: `work_minutes` from
  `analyze_work_day(...)['hours_worked']` (0 when it returns `None`),
  `total_minutes` (sum of complete entries), `earliest` / `latest` over
  every start and end present (including one-sided entries), `span_minutes`,
  and `missing_minutes` when `span - total > MISSING_THRESHOLD_MINUTES`
  (10), otherwise `None`.
- `tag_totals(entries) -> dict[str, timedelta]`: like
  `calculate_total_time_by_tag`, but keyed without `#` and counting each tag
  once per entry.
- `highlighted_totals(entries) -> list[tuple[label, timedelta]]` over
  `HIGHLIGHTED_TAGS`, a module constant of `(label, name)` pairs. A name that
  is a `TAG_GROUPS` key is totalled with `calculate_time_by_group`, which
  already counts an entry once per group. Any other name is a tag looked up
  in `tag_totals`. Zero totals are dropped.

The thresholds are module constants next to `HIGHLIGHTED_TAGS`, so making
them configurable later only touches where they're read.

`analyze_work_day` already does the plugin's work window and already
excludes `#personal`, `#off-task`, and `#break` (`NON_WORK_TAGS`), so it is
the `work duration` for both the day and the period.

Minutes are truncated (`int(seconds) // 60`), matching
`format_duration_long`. Sums are taken over `timedelta`s and truncated
once, so a period total doesn't lose a minute per entry.

### One period summary for weeks and longer periods

`_get_week_analyses` becomes `_load_days(root, start, end)`. It returns
`(date, entries | None)` for every day in the period, where `None` means no
daily note, and it reads notes via `_daily_note_path`. The period summary
aggregates those entries. The day report calls it with Monday..Sunday of
its day, and `--date` periods call it with START..END. `format_week_summary`
and the Mon–Fri loop are removed. Their tests are rewritten against the
new summary.

A day report reads its own note a second time for the week. Notes are
small, so nothing is cached.

*Alternative:* keeping `format_week_summary` for the day report and adding a
separate period formatter. That would leave two week layouts. The spec
(Q3) chose the Mon–Sun work-copy layout for both.

### Selecting the report

`time_report.py` parses `file` (now optional) and `--date` with argparse.
Both together is an error, and neither means `--date` today. `--date` goes
through `period.parse_period`, and a `ValueError` becomes `Error: <message>`
on stderr with exit 1. With `--date` the notes root is the current
directory, like `find_tasks.py`. With a file it is still derived from the
path via `_find_notes_root`. A single-day `--date` whose note doesn't exist
fails with `Daily note not found: <path>`.

The CLI side is `scripts/meta_notes/time.py`, the `query.py` counterpart.
`run(root, date_text) -> (lines, data)` does the same selection, raising
`ValueError` for the CLI to turn into `CliError`. `cmd_time` in `cli.py`
returns `Output(data | {"report": "\n".join(lines)}, lines)`. The parser
entry follows `tasks`: `--date`, the common `--json` / `--root`, and it
resolves the root.

### JSON shape

```
day report:    {start, end, kind: "day", file,
                items: [entry | gap | overlap],
                totals: {work_minutes, total_minutes, earliest, latest,
                         span_minutes, missing_minutes},
                by_tag: {tag: minutes}, work_vs_nonwork: {...},
                plan_adherence: {...} | null, week: <period>, report}
period report: {start, end, kind: "period", ...<period>, report}
<period>:      {start, end, work_minutes, total_minutes,
                highlighted: [{label, minutes}], by_tag: {tag: minutes},
                days: [{date, weekday, logged: bool, work_minutes,
                        earliest, latest, span_minutes}]}
entry:         {kind: "entry", line, text, start, end, minutes, tags}
```

`line` is the entry's 1-based line number, so agents can jump to it. Gap
and overlap items carry `start` and `end` in the same order the text shows
(earlier end, then later start).

### Vim calls the CLI

`meta_notes#time_tracking#ShowReport` keeps its daily-note and saved-file
checks. It takes the date from the filename (`\d{4}-\d{2}-\d{2}`), then calls
`meta_notes#cli#Run(['time', '--date', l:date])`. On `!ok` it shows the
error with `echohl ErrorMsg` instead of `echoerr`, so no exception is
raised. It puts `l:result.report` into the existing `Time Report` buffer.
`ExecutePythonScript` is no longer used here. `cli#Run` passes `--root
getcwd()`, which matches how the other CLI-backed commands behave.

## Risks / Trade-offs

- [The week summary layout changes: `hours worked` and `Weekly total worked`
  go away] → Users of the old text see a new format. Documented in
  `doc/meta-notes.txt`. The day totals keep the same work-window rules, so
  only the labels and span change.
- [Year periods read up to 366 notes and print 366 day lines] → Reading is
  cheap for plain files. The long listing is accepted (spec: every day
  gets an item).
- [Vim's cwd isn't the notes root when the report is run] → Same constraint
  as every other CLI-backed command. The CLI error says so.
- [Entries crossing midnight or dated in another day's note] → Durations
  already come from `calculate_duration` over full datetimes, and gaps
  subtract datetimes too, so a full-date end after midnight gives the right
  minutes. Entries are counted on the day of the note they're in.
- [Depends on `find-tasks-enhancements` landing first] → `period.py` and
  `tags.py` are imported directly, so implementation waits for that change
  to be archived.
