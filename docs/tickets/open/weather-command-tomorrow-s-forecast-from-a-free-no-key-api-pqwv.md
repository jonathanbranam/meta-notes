---
id: pqwv
title: "Weather command: tomorrow's forecast from a free no-key API"
kind: feature
opened: 2026-10-07
repos: [meta-notes]
changes: []
specs: []
needs: []
see: []
tasks: []
---

## The ask

## The ask

From the human, via the notes advisor (notes m-0119), 2026-10-06 21:36
EDT:

> let's find a standard way to get the weather. I think I'd like to just
> build a little API call into Notetaker. I think that's a useful thing to
> just have an automated command in there. I don't know how many different
> ways there are to get the weather, but we just take a standard API that
> works with no key, just something free, and fetch it. We should have that
> as a command that is in the built-in daily note. It'd be pretty nice. It
> would require setting your location in configuration.

And:

> That's a good part of our shutdown every evening: to check the weather
> for the next day.

## Notes from the advisor

- Open-Meteo (`api.open-meteo.com/v1/forecast`) needs no key and gives
  daily and hourly temperature, precipitation amount and probability,
  Fahrenheit and inch units, and a timezone. The advisor used it on
  2026-10-06 for Mason, OH and home.
- NWS `api.weather.gov` is a US-only, no-key alternative (it needs a
  User-Agent).

## Proposed shape (orchestrator's recommendation, for review)

- **API:** Open-Meteo. No key, worldwide, simple JSON; Python's standard
  library is enough (no new dependency).
- **Config:** a `[weather]` table in `.meta-notes`, like `[calendar]`:
  `latitude`, `longitude`, an optional `name` for display, and `units`
  (default Fahrenheit and inches). Lat/lon, not a place name: a place name
  needs a second (geocoding) call; `init` or the docs can show how to look
  them up.
- **Command:** `meta-notes weather [--date DAY]`, default tomorrow, with
  `--json`. Prints one line for the day (high/low, precipitation chance and
  amount, a short description) and fails clearly with no network or no
  `[weather]` table.
- **Daily note and evening routine:** the `daily-shutdown` skill (work)
  and `daily-plan` (personal, which has no shutdown) run it for tomorrow
  and put the line in tomorrow's daily note. Not a template `{{% vim %}}`
  block: opening a note shouldn't need the network.

## Questions for the human

1. Open-Meteo, lat/lon in `.meta-notes`, Fahrenheit: OK? (Recommended.)
2. Where does the forecast line go: tomorrow's daily note (recommended)
   or tonight's, and under which heading?
3. Several places (the advisor checked Mason and home): one `[weather]`
   location for now (recommended, YAGNI), or a list?
