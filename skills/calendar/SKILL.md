---
name: calendar
description: Answer questions about the user's calendar and meetings from their Google Calendar export in a meta-notes notes root. Use when the user asks whom they meet ("do I have a 1-1 with Zach next week?", "find any meetings with Loan Bui"), about meetings on a topic ("find all meetings about EFP"), when a meeting is, what's on a day, or when they're free. It does not plan a day or week (daily-plan, weekly-plan).
---

# Calendar

Answer a question about the user's meetings with one or two
`meta-notes calendar --json` lookups. Read-only: never edit notes, tasks,
or the calendar, and never read the export or cache files directly.

## Start

Run `command -v meta-notes`. If it prints nothing, stop and tell the
user: "`meta-notes` isn't on your PATH. Link the plugin's
`bin/meta-notes` into a directory on your PATH, for example
`ln -s <plugin>/bin/meta-notes ~/bin/meta-notes`." Don't run anything
else.

This skill reads no notes, so it doesn't run `meta-notes conventions`.

## Period

Turn the question's time words into a `--date` PERIOD, using today's
date (`date +%F`). Workweeks are Monday to Friday.

| The user says | PERIOD |
|---------------|--------|
| today, tomorrow | that day, `YYYY-MM-DD` |
| a weekday ("Thursday") | its next occurrence, today included |
| this week | Monday..Friday of the current week |
| next week | Monday..Friday of the following week |
| this month, next month | `YYYY-MM` |
| a date or range | `YYYY-MM-DD` or `YYYY-MM-DD..YYYY-MM-DD` |
| nothing | today and the 27 days after it (28 days) |

Always say which period you searched ("Searched 2026-09-25 to
2026-10-22.").

## Run

Pass names and topics as the user gave them, quoted.

- People: `meta-notes calendar --date <PERIOD> --with "<name>" --json`.
  Repeat `--with` for meetings with several people.
- Topics: `meta-notes calendar --date <PERIOD> --search "<text>" --json`.
  It matches title, location, and description, ignoring case, as typed.
- Both: combine `--with` and `--search`; an event must match all of them.
- What's on a day, or free time: no filter,
  `meta-notes calendar --date <PERIOD> --json`.

For example, on Friday 2026-09-25, "find any meetings with Loan Bui next
week" runs
`meta-notes calendar --date 2026-09-28..2026-10-02 --with "Loan Bui" --json`,
and "find all meetings about EFP" runs
`meta-notes calendar --date 2026-09-25..2026-10-22 --search EFP --json`.

Filtered output lists only days with a matching event. Each event has
`title`, `start`, `end`, `all_day`, `organizer`, `attendee_count`,
`attendees` (the first 20 only), `response` (the user's: `yes`, `maybe`,
`no-reply`, or null), `mine` (the user organized it), and `matches`:
`matches.with[].people` are the people each name matched, even past the
first 20, and `matches.search[].fields` says where each text matched.

## People

- `--with` matches word starts of names and emails, not nicknames:
  `zach` finds `Zachary Kim`; `Bob` doesn't find `Robert`.
- Nothing found for a full name: retry once with the first name alone.
  If that matches, say whom it matched ("No 'Loan Bui'; found Loan
  Nguyen").
- One name matched different people (different `email`s across
  `matches.with[].people`): list each person with their meetings, or ask
  which one the user meant.

## Topics

Nothing found for a `--search`: say so. You may retry once with a close
variant, such as an acronym's expanded form, and name it ("Nothing for
EFP; searched 'Enterprise Funding Platform' too").

## 1-1s

An event is a 1-1 with a person when it matches `--with` for them and
either:

- `attendee_count` is 2, or
- its title contains `1:1`, `1-1`, `1on1`, `1 on 1`, or `one on one`
  (ignoring case) and `attendee_count` is 3 or less.

For "do I have a 1-1 with X", search with `--with "X"` only (not
`--search 1:1`), then apply this rule. If there's no 1-1, say so and
mention any group meetings with X that were found.

## Free time

From an unfiltered agenda, list the gaps between timed events within the
workday (8:00 to 17:00 unless the user says otherwise). All-day events
don't block time unless the title says the user is away.

## Answer

1. Answer the question first, in one line ("Yes: Wed 2026-09-30,
   10:00-10:30, Zach / Jon 1:1.").
2. List matching events one per line: day, time (or "all day"), title.
   Add `[maybe]` or `[no-reply]` when `response` is one of those. For a
   `--search` hit outside the title, say where it matched
   ("description mentions EFP").
3. State the period searched.
4. Say how old the export is from `source.age_days` ("Export is 1 day
   old."). Pass on each of `warnings`; for a stale export, say it's N
   days old and may miss recent changes.

Keep it short. Don't print attendee lists unless asked.

## When the command fails

`ok` false:

- Calendar support isn't installed: tell the user to run the command the
  error names (`meta-notes init`, or `meta-notes init --force`) in the
  notes root, then you'll re-run the lookup.
- Otherwise (for example, no export): tell the user to export from Google
  Calendar (Settings, Import & export, Export) and save the `.zip` into
  the `ics/` folder the error names, then you'll re-run the lookup; or
  they can share a screenshot of the calendar instead.
- An invalid `--date` or `--with`: fix the arguments and re-run once.
