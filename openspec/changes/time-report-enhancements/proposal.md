## Why

Time reports can't show a day's log with the gaps and overlaps between
entries or how much of the day went unlogged. They also can't show where the
week's time went by tag, or be run for a date without typing the daily note's
path. There is no CLI command for them either, so agents and skills can't
read them.

The work notes repo still keeps its own `time_log.py`, which predates the
plugin and does most of this. `docs/Port tasks and time_log features into
meta-notes.md` lists what it does that the plugin doesn't. Porting those
features lets that repo delete its copy, so there is one implementation. The
task half of that document is in `find-tasks-enhancements`.

## Dependencies

- **`time-log-hhmm-format`** (archived 2026-09-25) added the `time-log`
  capability (entry syntax and timestamp formats). Nothing blocks.
- **`cli-core`** (archived) provides the CLI package, root resolution, and
  `--json` conventions that `meta-notes time` follows.
- **`find-tasks-enhancements`** adds the shared `--date` parser
  (`scripts/period.py`, `date-period` capability) and the shared tag parser
  and aliases (`scripts/tags.py`). Start after it is archived.

## What Changes

- **`meta-notes time [--date DATE] [--json]`.** New CLI command. `--date`
  uses the shared `date-period` syntax (default today). For a single day it
  prints that day's report. For a period (`START..END`, `YYYY-MM`,
  `YYYY-Qn`, `YYYY`) it totals the time logs across the period's daily
  notes, by tag and by day, and lists days with no log. This replaces the
  `meta-notes time-report --from --to` command proposed in
  `planning-skills`. `--json` returns the entries, gaps and overlaps,
  totals, and summaries as structured data.
- **`--date` on `time_report.py`.** Same syntax. The script finds daily
  notes with the existing `_daily_note_path` helper. The positional file
  argument keeps working.
- **Day log listing.** The report lists the day's log entries in order. Each
  shows its original activity line, then the parsed `start`, `end`, computed
  `time` (`H hr M min` / `M min`), and `tags`. A missing start or end prints
  `*MISSING START TIME*` / `*MISSING END TIME*` instead of a duration.
- **Gaps and overlaps.** Between consecutive entries, a gap of more than 2
  minutes is listed as a `*GAP of N min*` pseudo-entry, and a negative gap
  as `*Overlap of N min*`, with the earlier entry's end shown before the
  later entry's start. Both come from one entry-to-entry calculation.
- **Missing time.** The day total compares the span from the earliest start
  to the latest end against the sum of logged durations. When the difference
  exceeds 10 minutes, it is reported as `*missing time*`.
- **Weekly time by tag.** The week summary gains the total time per tag for
  the whole week, sorted alphabetically. Above it is a short list of
  highlighted tags with display labels, showing only tags that have time. The
  highlighted list is configurable rather than hard-coded. The work copy's
  list is `meeting` → "all meetings", `recruiting`, `agile`, `fence`,
  `iceberg`, `code`, `integr-test`, `axe`, `off-task`.
- The 2-minute gap and 10-minute missing-time thresholds are the local
  script's values. They are hard-coded unless open question 2 decides
  otherwise.

### Out of scope

- Deleting the work repo's `time_log.py` and `notes.py`, and fixing its
  stale daily-note path. That happens in the notes repo once this change
  ships.

## Capabilities

### New Capabilities
- `time-report`: `meta-notes time` and `time_report.py --date`; the day log
  listing with gaps, overlaps, and missing time; and the weekly per-tag and
  highlighted-tag summary. Entry syntax and timestamp formats stay in
  `time-log`.

### Modified Capabilities
- `cli`: adds the `time` subcommand.

## Open Questions

**Please resolve these before design and specs are written.**

1. **Highlighted-tag config.** Where does the highlighted-tag list live?
   Options: a `[time]` section in the `.meta-notes` sentinel, a separate file
   in the notes root, or a Vim global passed to the script. The Vim global
   wouldn't reach `meta-notes time`.
2. **Thresholds.** Are the fixed 2-minute gap and 10-minute missing-time
   thresholds fine, or should they be configurable alongside the tag list?
3. **Week span and totals.** The plugin's week summary covers Mon–Fri and
   reports "hours worked" with its work-window rules (leading and trailing
   `#personal` stripped, `#break` and `#off-task` not counted). The work copy
   covers Mon–Sun and reports "work duration" and "total duration". Which
   span and definitions win? Should the weekly tag totals and the day
   listing's missing time both use the plugin's work window?
4. **Report layout.** The work copy prints the day log followed by the week
   summary. The plugin prints time by tag, work vs. non-work, plan
   adherence, and the week summary. Where does the day log listing go, and
   do any existing sections drop?
5. **Tag aliases in weekly totals.** The plugin expands `#mtg` → `#meeting`
   and `#pers`/`#per` → `#personal`, and groups tags (`TAG_GROUPS`). Should
   the weekly per-tag totals use the expanded tags, and should highlighted
   tags be able to name a group (for example "all meetings")?
6. **Vim command.** Should `:MetaNotesTimeReport` switch to `meta-notes time`
   (passing the note's date), like the other commands that now call the CLI?

## Impact

- `scripts/time_tracking.py`: consecutive-entry gap/overlap, missing time,
  weekly per-tag totals
- `scripts/time_report.py`: `--date`, day log listing, weekly tag sections,
  highlighted-tag config
- `scripts/meta_notes/cli.py` and a new `scripts/meta_notes/time.py`:
  `time` subcommand and JSON output
- `autoload/meta_notes/time_tracking.vim`: may call the CLI (question 6)
- Tests: `test/unit/test_time_tracking.py`, a new `test_time_report.py`,
  `test_cli.py`
- `doc/meta-notes.txt`: `meta-notes time` and the report sections
- README command-line section: `meta-notes time`
