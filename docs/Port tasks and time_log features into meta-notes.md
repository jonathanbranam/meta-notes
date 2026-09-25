# project/meta-notes/Port tasks and time_log features into meta-notes

## Background

This notes repo has two local scripts, `tasks.py` and `time_log.py`, that
predate the meta-notes vim plugin. The plugin now ships its own, more
modular versions of the same ideas: task listing is split across
`tasks.py` (parsing) and `find_tasks.py` (CLI/report), and time tracking is
split across `time_tracking.py` (parsing) and `time_report.py`
(CLI/report). The daily note template
(`resource/template/daily.md`) already calls the meta-notes
`find_tasks.py` script, so the intent is clearly to move onto the
meta-notes versions going forward.

However, the meta-notes versions are missing several behaviors that the
local `tasks.py` and `time_log.py` still have. This note lists the gaps so
the meta-notes scripts can be brought up to parity (and eventually let us
delete the local duplicates).

## Tasks: what to add to meta-notes `tasks.py` / `find_tasks.py`

The local CLI is invoked as:

```
python3 tasks.py [--by-tag [TAG,...]] [--by-due-date [YYYY-MM-DD]]
```

With no options, it prints every section described below, one after
another. `--by-tag` alone prints only the "Tasks by tag" section;
`--by-tag admin,cd` restricts that section to just the `admin` and `cd`
tags. `--by-due-date` alone prints only the "Tasks by filename to start or
past due date" section for today; `--by-due-date 2026-09-25` prints it as
of that date instead.

1. **Track tags on each task.** The meta-notes `Task` record currently has
   no place to store the hashtags found on a task line. The local version
   extracts every `#tag` from the line using the regex `#([\w_-]+)` (so
   letters, digits, underscore, and hyphen) and stores the list on the
   task as `tags`. A task can have multiple tags, and they can appear
   anywhere in the line — before or after the description text, e.g.:

   ```
   - [ ] #admin follow up on fitness coach 📅 2026-06-10 Wed
   - [ ] #aftr #design follow up on UA stage utils 📅 2026-07-08 Wed
   ```

   gives `tags = ["admin"]` and `tags = ["aftr", "design"]` respectively
   (tags are stored without the leading `#`). This is needed for several
   of the items below and should be added to the task parsing step.

2. **Understand a `#later` tag.** In the local version, a task tagged
   `#later` is excluded from the normal "ready" listings (item 3 below)
   and only shows up in a separate "Tasks for later" section, and even
   then only once its start or due date has actually arrived (a
   `#later`-tagged task with a due date next year still won't appear).
   Concretely: `is_current()` returns false if the task has the tag
   `later`; a task is "ready" only if it's current, and "later" only if
   it's *not* current, in both cases requiring the due date or start date
   to be on or before the reference date. Meta-notes has no concept of
   this tag at all right now — every task with a date is treated the
   same regardless of tags. Example of the "Tasks for later" section (only
   printed when no filter flags are given):

   ```
   ## Tasks for later

   [[area/c1-career/CTML Mentorship]]
   - [ ] #later put a picture to it; fill out the DE template 📅 2025-06-11 Wed
   [[project/tasks/Miscellaneous]]
   - [ ] #later add FENCE (and SLEET) to CTML ML Models 📅 2024-07-05 Fri
   - [ ] #later file notes on integration testing from Tanul, et al 📅 2024-07-05 Fri
   ```

3. **Add a "ready" concept based on due/start date vs. a reference date.**
   The local version considers a task "ready" if its due date or its
   start date is on or before a given reference date (today, unless
   `--by-due-date` overrides it), and it does *not* have the `#later` tag.
   This is a simple `due_date <= for_date or start_date <= for_date`
   check, distinct from the meta-notes categorization, which instead
   buckets tasks into "due this week or earlier," "due later than this
   week," or "no date" based on the end of the current week. Meta-notes
   should gain this simpler due-or-start "ready by this date" comparison,
   since it drives items 2 and 4, and because "ready to start" is a
   sharper cutoff than "sometime this week." Example output (the "Tasks by
   filename to start or past due date" section), grouped by file with the
   raw task-list-item text (including its original bullet/checkbox marker
   and indentation) printed as-is under each file link:

   ```
   ## Tasks by filename to start or past due date

   [[area/ctml-design/Home]]
   - [ ] #aftr #design follow up on UA stage utils 📅 2026-07-08 Wed
   [[area/sapna-org/Fraud Leaders Forum - 2025]]
     * [ ] #iiyd read Arjun "The X factor" 📅 2025-04-16 Wed
   [[project/continuous-deployment/Meetings & Notes]]
     * [ ] #cd surface the issue with project versioning 📅 2026-09-11 Fri
     * [ ] #cd define behavior / non-behavior changes 📅 2026-06-16 Tue
   - [ ] #file move notes to feature logic notes 📅 2025-10-31 Fri
   ```

4. **Add a "group tasks by tag" report.** The local version can print all
   ready tasks (as defined in item 3) grouped under an `### tagname`
   heading for each tag, sorted case-insensitively alphabetically, with
   untagged tasks collected into a final `### Not tagged` group that's
   always sorted last regardless of alphabetical order (done by sorting on
   a key that maps "Not tagged" to a string of `~` characters, which sorts
   after all normal letters). Within each tag's section, tasks are further
   grouped by their source file, printed as a file link followed by the
   raw task lines. `--by-tag` also accepts an optional comma-separated tag
   list (e.g. `--by-tag admin,cd`) to filter the section down to just
   those tags, skipping any tag not in the list. Meta-notes' `find_tasks.py`
   has no equivalent grouping — it only groups by file, never by tag. This
   should be added as a new report mode (for example, alongside the
   existing `--folder`/`--status`/`--due-*` filters), with a comparable
   "list only these tags" option. Example output (`--by-tag`, no filter):

   ```
   ## Tasks by tag

   ### admin

   [[resource/daily-notes/Daily Note 2026-06-10 Wed]]
   - [ ] #admin follow up on fitness coach 📅 2026-06-10 Wed
   [[resource/daily-notes/Daily Note 2026-06-30 Tue]]
   - [ ] #admin update CIDX / CT Day Two training with Zoom 📅 2026-06-30 Tue
   [[resource/daily-notes/Daily Note 2026-08-31 Mon]]
   - [/] #admin review case manager issues 📅 2026-08-31 Mon

   ### aftr

   [[area/ctml-design/Home]]
   - [ ] #aftr #design follow up on UA stage utils 📅 2026-07-08 Wed
   ```

   (further tag sections continue alphabetically, ending with `### Not tagged`
   if there are any untagged ready tasks).

5. **Decide how this interacts with the existing week-based
   categorization.** Once "ready" and tag-grouping exist, we'll have two
   different ways of slicing tasks by date (week-based buckets vs. simple
   due-or-start-by-date). Worth deciding whether to keep both as separate
   report modes or replace the week-based categorization with the simpler
   one — the daily/weekly templates should guide which is more useful in
   practice.

## Time tracking: what to add to meta-notes `time_tracking.py` / `time_report.py`

The local CLI is invoked as:

```
python3 time_log.py [--date YYYY-MM-DD]
```

and always prints the same two sections: the single day's time log (for
`--date`, or today) followed by that day's week-summary (Monday through
Sunday of the week containing that date).

Each time log entry, when printed, shows its original list-item text
(e.g. `- review #horz position paper`) followed by indented `* start:`,
`* end:`, `* time:`, and `* tags:` lines that the script recomputed from
parsing — `* time:` is the computed duration in `H hr M min` / `M min`
form, and `* tags:` is a space-separated list of the tags found (without
the `#`), for example:

```
- review #horz position paper
  * start: 09:45
  * end:   10:35
  * time:  50 min
  * tags:  horz
```

If a start or end time is missing from the note, it's printed as
`*MISSING START TIME*` / `*MISSING END TIME*` instead of a duration.

1. **Detect gaps between log entries.** The local version walks through a
   day's log entries in order and, for any gap greater than 2 minutes
   between when one entry ends and the next one starts, prints an extra
   pseudo-entry between them:

   ```
   - June DMC Connect
     * start: 15:00
     * end:   15:50
     * time:  50 min
   - *GAP of 10 min*
     * start: 15:50
     * end:   16:00
   - Tanul & Melissa
     * start: 16:00
     * end:   16:40
     * time:  40 min
   ```

   Meta-notes' time tracking module has no equivalent — it never compares
   one entry's end time to the next entry's start time.

2. **Detect overlapping log entries.** Similarly, if one entry starts
   before the previous one has ended (i.e. the gap is negative), the local
   version prints an `*Overlap of N min*` pseudo-entry instead of a gap,
   showing the previous entry's end time first and the new entry's start
   time second (so the two times are in the opposite order from a normal
   entry, which is the visual cue that it's an overlap, not a gap):

   ```
   - *Overlap of 9 min*
     * start: 14:39
     * end:   14:30
   - Chris Sparks fraud ring preso
   ```

   This should be added alongside the gap detection above, since both
   come from the same entry-to-entry comparison (a single "gap in
   minutes" calculation that's positive for a gap and negative for an
   overlap).

3. **Detect and report "missing" time.** At the end of the day's log, the
   local version computes the total time span for the day (latest end
   time minus earliest start time recorded anywhere that day), compares
   it to the sum of all logged entry durations, and — only if the
   difference exceeds 10 minutes — prints it as a `*missing time*` line in
   the "Total Time" section:

   ```
   ### Total Time

   - work duration:    9 hr 6 min
   - total duration:   9 hr 6 min
   - earliest time:    07:08
   - latest time:      17:51
   - total time:       10 hr 43 min
   - *missing time*:   1 hr 37 min
   ```

   This surfaces time that wasn't logged at all (e.g. entries with a
   missing end time break the chain, as seen above where two entries had
   `*MISSING END TIME*`/`*MISSING START TIME*`). Meta-notes has no
   equivalent calculation today.

4. **Let the report be generated for an arbitrary date, not just an
   explicit file.** The local `time_log.py` accepts `--date YYYY-MM-DD`
   (defaulting to today) and resolves the daily note's path itself from
   that date; meta-notes' `time_report.py` only takes a file path directly
   as its positional argument (it does construct daily-note paths
   internally already, for the week-summary lookups — see
   `_daily_note_path` in `time_report.py` — so the pattern exists, it just
   isn't exposed as a way to select the report's main day). Adding a
   `--date` option that resolves to the matching daily note using that
   same helper would remove the need to know or type the exact file path,
   e.g. `python3 time_report.py --date 2026-09-22` instead of
   `python3 time_report.py "plan/daily/26-Q3/2026-09-22 Tue.md"`.

5. **Add a fuller weekly time-by-tag breakdown.** The local weekly report
   ends with three parts: a short curated list of specific tags shown
   with friendlier display names right under "Total Time" (only tags that
   have any time are shown), then the full per-tag breakdown sorted
   alphabetically by tag, then the day-by-day summary. For example:

   ```
   ## Summary for Week 2026-09-21 to 2026-09-27

   ### Total Time

   - work duration:    10 hr 34 min
   - all meetings:     2 hr 25 min
   - recruiting:       22 min

   ### Time per tag

   - break:            20 min
   - dax-sdd:          30 min
   - email:            37 min
   - horz:             2 hr 20 min
   - meeeting:         30 min
   - meeting:          2 hr 25 min
   - personal:         2 hr 52 min
   - raft:             1 hr 5 min
   - recruiting:       22 min

   ### Day Summaries

   - 2026-09-21 Mon
     * work duration:    52 min
     * earliest time:    08:00
     * latest time:      10:37
     * total time:       2 hr 37 min
   ```

   The curated list in the local script is hard-coded to these tag names
   and display labels, in this order: `meeting` → "all meetings",
   `recruiting` → "recruiting", `agile` → "agile", `fence` → "fence",
   `iceberg` → "iceberg", `code` → "code", `integr-test` → "integr-test",
   `axe` → "axe", `off-task` → "off-task". Meta-notes' week summary
   currently only reports hours worked and total time per day — it
   doesn't roll up time by tag across the week at all (neither the full
   alphabetical breakdown nor the curated list). This should be added,
   ideally with the curated "important tags" list made configurable
   rather than hard-coded to this repo's specific tag vocabulary, since
   meta-notes is meant to be reusable across different notes setups.

## Cleanup once these are ported

- The local `notes.py` still points at a stale daily-note location
  (`resource/daily-notes/Daily Note YYYY-MM-DD Www.md`), but daily notes
  actually live at `plan/daily/YY-QN/YYYY-MM-DD Www.md` (see
  `resource/template/daily.md` and the `_daily_note_path` helper already
  in meta-notes' `time_report.py`, which uses the correct pattern). Once
  the local scripts are retired, this discrepancy goes away on its own;
  if they stick around any longer, this constant should be fixed so
  `time_log.py`'s `--date` option actually finds the right file.
- Once the above items are ported, the local `tasks.py` and `time_log.py`
  (and their shared `notes.py` helpers) can likely be deleted in favor of
  the meta-notes plugin scripts, and the templates updated to call the
  meta-notes equivalents everywhere.
