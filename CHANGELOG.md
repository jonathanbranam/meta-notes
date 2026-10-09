# Changelog

What changed for users of the meta-notes plugin and CLI: new functionality,
and changes to options and existing behaviour. Newest first. Internal changes
(tests, refactors, docs only) are left out. Entries start at 2.0.0.

Every version bump adds an entry here (see `.bridle/rules/versioning.md`).

## 2.31.0 - 2026-10-09

- Fixed: with autosave or autoreload on, a manual `:w` of a notes buffer
  whose file changed on disk is refused first, with a diff of disk against
  your buffer; an open diff is refreshed (and you are told) when the file
  changes again. The conflict diff also no longer drops the file's first line.

## 2.30.0 - 2026-10-08

- Changed: calendar `downloads` now takes one setting, a folder and a glob
  (`downloads = "~/Downloads/Google*.zip"`). Replace `downloads` plus
  `downloads_pattern` with it; the old pair still works.
- Changed: an export is copied only when it is newer than the newest cached
  one and its SHA-256 is new, and the original is deleted where allowed.

## 2.29.1 - 2026-10-08

- Fixed: a daily note's `### Outlook` section has a blank line after the
  heading, and `outlook refresh` tolerates missing or extra blank lines.

## 2.29.0 - 2026-10-07

- Added: `meta-notes outlook refresh` rewrites the Outlook section in today's
  and tomorrow's notes, keeping lines you added. The `daily-plan` skill runs it.

## 2.28.1 - 2026-10-07

- Fixed: the `### Time Block` heading keeps its markdown highlight.

## 2.28.0 - 2026-10-07

- Added: `meta-notes outlook`, a day's weather, temperature sparkline, sun
  times and National Weather Service alerts for a place. Set `[outlook]` in
  `.meta-notes`; each line has an on/off switch.

## 2.27.0 - 2026-10-07

- Added: `meta-notes calendar` picks up Google Calendar exports from your
  browser's downloads folder and moves them into the cache.

## 2.26.8 - 2026-10-07

- Fixed: `time-log update` treats an empty `end:` line as an open entry.

## 2.26.7 - 2026-10-06

- Fixed: `time-log append` accepts tilde times (`~HH:MM`) in `--start`,
  `--end`, `--prev-start` and `--close-prev`.

## 2.26.6 - 2026-10-06

- Fixed: `task add` accepts `--due undated` (and `none`), like `task update`.

## 2.26.5 - 2026-10-06

- Changed: an event's end-time row in the Time Block is never filled; the end
  time is exclusive.

## 2.26.4 - 2026-10-06

- Fixed: `task add` leaves a blank line after a task inserted below an H1 that
  already has a blank line after it.

## 2.26.3 - 2026-10-06

- Fixed: `task add` leaves a blank line after a task inserted below the H1.

## 2.26.2 - 2026-10-06

- Changed: "no plan" in a Time Block is struck through (`~no plan~`).

## 2.26.1 - 2026-10-06

- Changed: `task add` puts the task at the end of the `## Tasks` section (any
  heading level), or below the H1 when there is none.

## 2.26.0 - 2026-10-06

- Changed: `task update` finds the line by `--expect` when `:LINE` is omitted.

## 2.25.2 - 2026-10-05

- Fixed: the task query lists every task line again (2.24.1's skip of
  daily-note snapshot sections is removed).

## 2.25.1 - 2026-10-05

- Fixed: the snapshot skip hid too much; it only hid copies under a top-level
  link bullet. (Removed in 2.25.2.)

## 2.25.0 - 2026-10-05

- Added: `meta-notes tasks --agenda`, a preset for overdue, today and each day
  ahead.

## 2.24.1 - 2026-10-05

- Changed: the task query skips daily-note snapshot sections. (Reverted in
  2.25.2.)

## 2.24.0 - 2026-10-04

- Added: `meta-notes conventions --json` includes `tag_aliases`.

## 2.23.0 - 2026-10-04

- Added: `meta-notes ui start`, `stop`, `status`, `url` and `open` manage the
  meta-notes-ui server (`[ui] path` in `.meta-notes`).

## 2.22.0 - 2026-10-04

- Added: `meta-notes note write`, a race-safe edit of a note's lines.

## 2.21.0 - 2026-10-04

- Changed: an event fills every Time Block row it spans.

## 2.20.1 - 2026-10-04

- Fixed: NERDTree also refreshes when reopened or shown in another tab.

## 2.20.0 - 2026-10-04

- Added: a visible NERDTree stays current when files or folders change in a
  notes root. Set `g:meta_notes_nerdtree_refresh = 0` to turn it off.

## 2.19.0 - 2026-10-03

- Added: `meta-notes init --mode personal` writes the mode, installs
  `daily-personal.md` and suggests the personal `CLAUDE.md`.

## 2.18.0 - 2026-10-03

- Changed: ceremony skills follow the root mode. A personal root has no daily
  shutdown, reviews and plans weekly on Sunday and covers seven days.

## 2.17.0 - 2026-10-03

- Changed: working hours and days follow the root mode (work: 08:00 to 17:00,
  Monday to Friday; personal: 07:00 to 21:00, every day).

## 2.16.0 - 2026-10-03

- Changed: `meta-notes time` follows the root mode; a personal root counts
  untagged time as personal and `#work` as work.

## 2.15.0 - 2026-10-03

- Added: `mode = "work"` or `"personal"` in `.meta-notes` (default `work`),
  reported by `meta-notes prime`.

## 2.14.3 - 2026-10-03

- Fixed: guidance for unapproved plans: "no plan" goes in Plan, not Actual.

## 2.14.2 - 2026-10-03

- Changed: skills strike through only plans the human made or approved.

## 2.14.1 - 2026-10-03

- Changed: GitGutter is turned off for the whole session when Vim starts
  inside a notes root (still `g:meta_notes_disable_gitgutter`).

## 2.14.0 - 2026-10-03

- Added: GitGutter is turned off in notes buffers. Set
  `g:meta_notes_disable_gitgutter = 0` to leave it on.

## 2.13.1 - 2026-10-03

- Changed: Time Block text conventions: project names are lowercase, and
  replanning says what it pushes out.

## 2.13.0 - 2026-10-03

- Added: `meta-notes planning`, a per-day planning record (planned days,
  no-plan, crossed-out) for the weekly review.

## 2.12.5 - 2026-10-03

- Changed: conventions and the time-block and daily-shutdown skills record
  "no plan" rows.

## 2.12.4 - 2026-10-03

- Changed: conventions describe the tilde (`~`) times in the Time Block and
  Time Log.

## 2.12.3 - 2026-10-03

- Fixed: the time-block skill uses single tildes.

## 2.12.2 - 2026-10-03

- Added: the `time-block` skill, to plan, replan, fix or fill the Time Block
  and Time Log.

## 2.12.1 - 2026-10-03

- Fixed: `time-log update` reports one written entry per new entry.

## 2.12.0 - 2026-10-03

- Added: `meta-notes time-block replace` rewrites a range of rows. Plan and
  Actual columns are found by their header.

## 2.11.3 - 2026-10-02

- Changed: `meta-notes init` warns, with the install command, when the file
  watcher (`fswatch` or `inotifywait`) is missing.

## 2.11.2 - 2026-10-01

- Changed: task edits always write a done task as lowercase `x`; an existing
  `X` is kept.

## 2.11.1 - 2026-10-01

- Fixed: a parent task is marked done only when every subtask is done;
  otherwise it shows partial progress.

## 2.11.0 - 2026-10-01

- Added: `task notes`, `task replace` and `task add --under` write a task's
  notes and subtasks. A parent's status follows its subtasks.

## 2.10.0 - 2026-10-01

- Added: `meta-notes task show` reads one task with its notes and subtasks
  (`--tree`).

## 2.9.0 - 2026-10-01

- Added: `task update --text` changes a task's text.

## 2.8.2 - 2026-10-01

- Fixed: the reload notice is no longer swallowed by a silent `checktime`.

## 2.8.1 - 2026-10-01

- Fixed: the autoreload timer starts correctly and shows the reload notice.

## 2.8.0 - 2026-10-01

- Added: opt-in autosave and autoreload for notes buffers
  (`g:meta_notes_autosave`, `g:meta_notes_autoreload`,
  `g:meta_notes_checktime_interval`), with `:MetaNotesAutosave`,
  `:MetaNotesAutoreload` and `:MetaNotesAutoStatus`. A conflict keeps your
  buffer and opens a diff.

## 2.7.0 - 2026-10-01

- Added: `meta-notes time-log append` and `time-log update`.

## 2.6.1 - 2026-10-01

- Fixed: the time report's Work vs Non-Work split uses the work-duration rule.

## 2.6.0 - 2026-10-01

- Added: `meta-notes time-block update` edits Time Block cells.

## 2.5.0 - 2026-09-30

- Added: `meta-notes task add` creates a task line with due date, time and
  recurrence rule.

## 2.4.0 - 2026-09-30

- Changed: completing a recurring task inserts the next occurrence above it.
  `--no-recur` and `--recur` control it; `--json` reports what was created.

## 2.3.0 - 2026-09-30

- Added: `meta-notes tasks --at HH:MM|now` shows timed tasks overdue, due or
  future at a time of day.

## 2.2.0 - 2026-09-30

- Added: recurrence on tasks is read and reported (`recurrence` in
  `tasks --json`); an unsupported rule gives a warning.

## 2.1.0 - 2026-09-30

- Added: time of day on tasks (a time, or a date and time), shown in
  `tasks --json`, set with `task update --time`.

## 2.0.0 - 2026-09-30

- Starting point of this changelog.
