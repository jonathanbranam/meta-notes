+++
id = "mn-efc9"
title = "OOO event not detected as mine: organizer-less personal events need calendar_name == email"
kind = "bug"
state = "integrated"
created_at = "2026-09-28T23:49:27.385Z"
updated_at = "2026-09-29T01:48:36.227693Z"
+++

The human wants this fixed in the plugin. Their write-up follows verbatim.

Scope and decisions (orchestrator, KISS): an event with no ORGANIZER and no ATTENDEE is the users own when it comes from one of the calendars configured in `.meta-notes` `[calendar] calendars`; drop the `calendar_name == email` requirement. Treat every configured calendar as the users own for now (no owned/viewed split until a real shared calendar shows up); say so in the spec. Add a scenario to openspec/specs/calendar-agenda/spec.md and a pytest with this event (no ORGANIZER/ATTENDEE, X-WR-CALNAME WORK, email set). Behaviour change: bump PATCH. Done = ./run_tests.sh && pipenv run pytest test/unit/.

---

# project/meta-notes/OOO event not detected as mine

## Background

`meta-notes calendar --date 2026-09-28 --json` reported an all-day-ish
event titled "OOO" (2026-09-28 14:00–18:05 local) with `"mine": false`,
even though it's a personal event the user created on their own calendar
for an out-of-town appointment. The daily-plan skill then treated it as
someone else's event rather than blocking time on the user's own day.

## The event, as it appears in the .ics export

From `WORK_user@example.com.ics` (calendar `X-WR-CALNAME:WORK`):

```
DTSTART = 2026-09-28 18:00:00+00:00   (2:00pm America/New_York)
DTEND   = 2026-09-28 22:05:00+00:00   (6:05pm America/New_York)
DTSTAMP = 2026-09-28 13:43:38+00:00
UID     = abc123def456@google.com
CLASS   = PUBLIC
SEQUENCE = 0
STATUS  = CONFIRMED
SUMMARY = OOO
TRANSP  = OPAQUE
```

No `ORGANIZER` property and no `ATTENDEE` property at all — this is a
plain personal event with no invitees, the kind you create by just
clicking a blank slot on your own calendar and typing a title.

## Root cause

`attendance()` in the plugin (`scripts/meta_notes/calendar.py`,
around lines 512–538) computes `mine` like this:

```python
if organizer is not None:
    mine = bool(me) and _address(organizer).lower() == me
    ...
else:
    mine = bool(me) and not attendees and calendar_name.lower() == me
```

When `ORGANIZER` is absent (this event's case), it falls to the `else`
branch, which requires `calendar_name.lower() == me` — i.e. the *name*
of the source calendar must equal the configured email address.

In this notes root, `.meta-notes` has:

```toml
[calendar]
email = "user@example.com"
calendars = ["WORK"]
```

and the .ics file's `X-WR-CALNAME` is literally `WORK` — a short label,
not the account email. So `"work" == "user@example.com"` is
always false, and every organizer-less, attendee-less personal event on
this calendar comes back `mine: false`, regardless of who created it.

The comment in the Explore agent's report on this code suggests the
`else` branch's intent was already "no organizer + no attendees implies
it's a personal event on my own calendar" — the `calendar_name == me`
check was presumably meant as a safety check for some other scenario
(maybe distinguishing calendars other than the user's primary one, e.g.
a shared team calendar with no ORGANIZER on some entries), but it
mismatches how Google actually names a primary calendar's `X-WR-CALNAME`
(a short label like `C1`, not the account email).

## Suggested fix direction (for meta-notes plugin, not this repo)

Something like: if there's no `ORGANIZER` and no `ATTENDEE`, treat the
event as the user's own as long as it came from a calendar configured
under `calendars = [...]` in `.meta-notes` (i.e. one of the user's own
subscribed/owned calendars), rather than requiring the calendar's
*name* to equal the email. The `calendars` list in config already scopes
which calendars are "mine" to load; reusing that instead of comparing
against `calendar_name` would fix this without needing `X-WR-CALNAME` to
carry the email address.

Worth checking whether other calendars in `calendars = [...]` (if the
user ever adds more than `WORK`) could legitimately be *not* the user's
own (e.g. a shared team calendar they view but don't own) — if so, the
fix needs a way to distinguish "calendars I view" from "calendars I
own," which the current single `calendars` list may not support.

## Thread

### note · agent:manager · 2026-09-29T01:48:36.194Z
attendance() in scripts/meta_notes/calendar.py no longer takes calendar_name: an event with no organizer and no attendees is mine when email is set, whichever loaded calendar it is in. Every configured calendar counts as the user's own (no owned/viewed split, stated in the spec). Spec, doc and pytest updated. v0.13.1.

### note · agent:manager · 2026-09-29T01:48:36.227Z
integrated: a30f659
