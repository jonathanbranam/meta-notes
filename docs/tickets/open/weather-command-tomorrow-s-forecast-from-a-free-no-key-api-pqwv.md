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

## The human's answers, 2026-10-07 (to the meta-notes aide)

On the first round of questions:

> What are the questions? Also let's add sunrise and sunset as options.
> This should be a command that user can call from CLI and use existing
> template support to insert into document.

On the second round:

> Ah, interesting point. I used to create daily notes only on the day...
> the forecast is something that changes as the day gets closer...
>
> I think since we have sunrise as well let's call the command something
> more generic like local or location   Add some suggestions. Then params
> or sub command for weather or sunrise sunset
>
> IDK my lat long so I would prefer city state or zip code. Unit support
> is optional. Use F. One location configured in notes. CLI should accept
> location information so the agent can call for other locations during
> travel, etc.
>
> I want to review this again before working on it.

So, replacing the proposed shape where they differ:

- A CLI command the human runs; the daily template inserts its output
  through the existing `{{% … %}}` template support (not the shutdown or
  plan skills).
- Weather and sunrise/sunset, as subcommands or options of one command
  with a generic name (`local`, `location`, or a suggestion; not chosen).
- Location configured as city and state or a ZIP code (needs geocoding),
  one location in `.meta-notes`; the CLI also accepts a location so an
  agent can ask about other places when traveling.
- Fahrenheit; other units optional.
- Open: the forecast changes as the day nears, and a template block runs
  when the note is created (the human used to create daily notes only on
  the day). How fresh the note's forecast should be isn't decided.
- **Hold: the human wants to review the revised shape before work starts.**

## Revised shape (orchestrator, 2026-10-07, for the human's review)

- **Command name.** Suggestions: `local` (recommended: short, and the
  human's own word), `location` (reads like setting one), `place`,
  `outside`, `sky`. Below uses `local`.
- **Subcommands.** `meta-notes local weather` (high/low in F, chance and
  amount of rain, a short description) and `meta-notes local sun` (sunrise,
  sunset). Plain `meta-notes local` prints both; that's what the daily
  template uses. Options on all three: `--date DAY` (default today),
  `--location "Mason, OH"` or `--location 45040` (for travel; overrides the
  config), `--json`.
- **Config.** One location in `.meta-notes`:
  `[local]` with `location = "Mason, OH"` or `location = "45040"`. No
  lat/lon to look up.
- **API.** Open-Meteo for both steps, no key, standard library only:
  its geocoding search turns a ZIP or a city into coordinates (checked
  2026-10-07: `45040` and `Mason` with state Ohio both give Mason, OH), then
  its forecast gives the day's temperatures, rain, sunrise and sunset. The
  geocoded coordinates are cached in `.meta-notes-cache/`, so a configured
  place is looked up once. A city with no state that matches several places
  is an error that lists them.
- **Daily note.** `templates/daily.md` and `daily-personal.md` get a
  `{{% ... %}}` line running `meta-notes local --date {{date}}`, under a
  `### Weather` heading near the top (heading name open). With no `[local]`
  table or no network the line prints a short "weather unavailable:
  <reason>" instead, so creating a note never fails because of it.
- **Freshness (recommended: a snapshot).** The block runs once, when the
  note is created, and the line says when it was fetched ("as of 9:40 PM
  Tue"). A note made the evening before has a 12-hour-old forecast, which is
  fine for planning; for a newer one, run `meta-notes local` (or ask the
  agent) on the day. Not now (YAGNI): refreshing the note's line
  automatically, a skill step that rewrites it. Sunrise and sunset don't go
  stale.
- **Units.** Fahrenheit and inches only. Celsius is a later option if
  asked for.
- **Rejected:** lat/lon config (the human doesn't know theirs); NWS
  `api.weather.gov` (US only, needs a separate geocoder); Nominatim and
  zippopotam.us (a second service for what Open-Meteo already does); the
  shutdown or plan skills writing the line (the human chose the template).

### Questions for the human

1. Name `local`, with subcommands `weather` and `sun`? (Recommended.)
2. Freshness: a snapshot when the note is created, stamped with the fetch
   time, and the CLI for anything newer? (Recommended.)
