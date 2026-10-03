---
name: time-block
description: Edit the daily note's Time Block and Time Log in a meta-notes notes root. Use when the user asks to plan, replan, fix or fill the Time Block, or to record what they did instead of what was planned. It does not plan the whole day (daily-plan) or run check-ins (checkin).
---

# Time Block edits

Change the Time Block (Plan and Actual) and the Time Log for the user,
through the CLI and in their style. Time blocking is Cal Newport's: Plan is
what you meant to do; Actual records deviations and extras.

## Start

1. Run `command -v meta-notes`. If it prints nothing, stop and tell the
   user: "`meta-notes` isn't on your PATH. Link the plugin's
   `bin/meta-notes` into a directory on your PATH, for example
   `ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't read or edit
   any note.
2. Run `meta-notes conventions` and follow it. Follow the notes root's
   `CLAUDE.md` too: personal tags, working hours and the workout block are
   there, and it wins over this skill.
3. Run `meta-notes note daily [date]` for the note's path, and read its
   Time Block and `### Log` before changing anything.

## Hard rules

- Never edit the table or the log by hand; the user usually has the note
  open in Vim. Read first, and always pass `--expect` with the text you
  read. On a mismatch, re-read and retry, or ask.
- Replan only rows that haven't happened yet.
- Meetings start `mtg:`. Don't move or replace them.
- Keep `[brackets]`, `(parens)` and other prefixes (`train:`, `pers:`,
  `work:`, `(opt)`) as written. Never invent one; if the meaning matters,
  ask the user.
- Text is lowercase except proper names. Project names (bridle, meta-notes) stay lowercase. They aren't real sentences.
- No Markdown emphasis (`**`, `*`, `_`) in the table: Vim conceal breaks the
  column alignment. Tildes (below) are the one exception.
- Single tildes wrap an off-plan row's Plan. A tilde before a time means
  approximately (see `meta-notes conventions`).

## Commands

- `meta-notes time-block update <note> --time 9:30am [--through 10:15am]
  --plan <text>` (or `--actual`): one cell, or a range set to the same
  text. `--create` adds a missing row.
- `meta-notes time-block replace <note> --time 9:00am --through 10:00am
  --expect <rows> --text <rows>`: rewrites a range in one call (reorder,
  move, add a row). Every row of the range stays in `--text`.
- `meta-notes checkin actual <time> <text> [--through <time>]`: an Actual
  during check-ins; the `checkin` skill uses it.
- `meta-notes time-log append` and `time-log update`: the log, as in
  `meta-notes conventions`.

## Rules for the content

- **Replan**: rewrite the Plan of rows still ahead. One Plan column is
  enough. Check what the change pushes out: deadlines, pickups, leave-by times.
- **The plan happened**: leave Actual blank.
- **The plan didn't happen** (a row already past): don't change the Plan,
  it has happened. Wrap it in single tildes, `~write spec~`, and give
  Actual a short summary of what happened instead.
- **No plan was made** (a row already past with an empty Plan): set the
  Plan to `no plan` and give Actual a short summary of what happened.
- **Time Log**: the literal truth, to the minute. Actual is the short
  summary; the log has the detail.

## Finish

Tell the user in a line or two which rows changed. Offer nothing more.
