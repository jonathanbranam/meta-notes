---
id: kxxy
title: Working hours and days follow the root mode
kind: feature
opened: 2026-10-03
repos: [meta-notes]
changes: []
specs: []
needs: [47rb]
see: [zyab]
tasks: []
---

# Working hours and days follow the root mode

## The problem

Hours and days are written for work in many places: `prime.md:33-36`
("08:00 to 17:00, Monday to Friday; don't plan work after 17:00"),
`conventions.md:235` ("Workdays are Monday to Friday"), `checkin.py:17-18`
(`DEFAULT_END = "17:30"`, which doesn't match prime's 17:00), and the
daily template's Time Block (8:00am to 6:00pm, `templates/daily.md:37-77`)
and its "start work:" log line (:25). The personal root's `CLAUDE.md`
still says 08:00-17:00 Monday-Friday because it was copied from work, and
it's used most on weekends ("Replanning is common, especially on
weekends").

## Change, by mode

- **work**: unchanged; 08:00-17:00, Monday-Friday.
- **personal**: every day of the week; a longer day (span to decide); the
  log line "start day:"; no "don't plan work after 17:00".
- One source for the hours: `prime`, `conventions`, `checkin` (the
  `[checkin] end` key already exists) and the daily template read the same
  value, so 17:00 vs 17:30 can't drift again.

## Decided with the human, 2026-10-04

- Personal: 07:00 to 21:00, every day of the week, fixed by the mode (no
  `[day]` keys).
- Update the daily template for it: in a personal root the Time Block runs
  7:00am to 9:00pm and the log line is "start day:".
