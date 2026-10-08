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

## The human's answers, 2026-10-07 evening (to the meta-notes aide)

On the name, freshness and heading:

> ok, I'm not a huge fan of "local" suggest other options; also, yes I
> think we should update the weather information in a note over time, if
> it is created a few days ahead, we have a syntax output for the command
> I think and then exact match that and update it.
>
> '### Today' is good; ### Forecast ### Weather... hnmmmm

After the aide suggested almanac, day, forecast, outlook and today:

> ooo! outlook and almanac are both great. ### Outlook reads well too;
> ### Almanac idk

On what goes in it (the aide's list: core line always, extras only when
notable):

> Yeah, out of those, highs and lows are good. Rain and when is fantastic.
> Sunrise and sunset hours of sunshine. I think those all sound really
> good, and I'll go with that for now.
>
> I think the only other thing that I get interested in is when the high
> is and when the low is, but this is going to be way too much information
> to put in every note. Super weather lights are good. Other things I don't
> really care about: pollen, moon phase, and first frost. I'm not gardening
> right now, but when I am, that's nice. Snow amount is the same as rain
> amount. If there's snow, show that.

("Super weather lights" is speech-to-text for severe weather alerts.)

> I really want to check the weather the day ahead, always.
>
> I think we're going to start creating those daily notes a day or two in
> advance.

So, replacing the revised shape where they differ:

- **Name:** `meta-notes outlook` (subcommands `weather` and `sun`; plain
  `outlook` prints both), writing a `### Outlook` section in the daily
  templates.
- **Content:** high and low; rain chance, amount and when ("rain after
  3 PM"); snow amount when there's snow; sunshine (hours or sunny/cloudy);
  sunrise and sunset; severe weather alerts only when there is one (NWS,
  US only). Not now: times of the high and low (too much for every note;
  maybe in `--json` or a detail view), wind, UV, air quality, pollen,
  moon phase, frost.
- **Refreshing:** the line has a fixed, exactly-matchable format with an
  "as of" time; `meta-notes outlook --update <note>` replaces it in place
  (race-safe write; no change and a message when the line isn't there).
  Daily notes will often be made a day or two ahead, so the refresh
  matters; the aide suggested daily-plan run it on the day's and the next
  day's notes. Not decided who runs it.
- **Hold:** the orchestrator revises the shape once more for the human's
  look before work starts.

## Revised shape, round 3 (orchestrator, 2026-10-08, for the human's review)

Everything from round 2 that the human didn't change still holds: Open-Meteo
for geocoding and the forecast, no key, standard library only; one location
in `.meta-notes`; `--location` for travel; Fahrenheit and inches.

- **Commands.**
  - `meta-notes outlook [--date DAY] [--location PLACE] [--json]` prints
    the Outlook lines (below). `--date` defaults to today.
  - `meta-notes outlook weather` and `meta-notes outlook sun` print only
    their line.
  - `meta-notes outlook --update <note>` refetches for the note's date and
    replaces its Outlook lines in place (race-safe, like `note write`).
    When the note has no Outlook lines it changes nothing and says so.
- **Config.** `[outlook]` in `.meta-notes`, `location = "Mason, OH"` or
  `location = "45040"`.
- **What the note gets.** A `### Outlook` section in `templates/daily.md`
  and `daily-personal.md`, filled by
  `{{% python scripts/... --date {{date:%Y-%m-%d}} %}}` (the existing
  template support), near the top. Example:

      ### Outlook
      - Weather: 72/55 F, rain 60% 3-8 PM 0.3 in, 4 h sun (as of 9:40 PM Tue)
      - Sun: up 7:41 AM, down 7:02 PM
      - Alert: Severe Thunderstorm Warning until 6:00 PM

  - Rain shows only when the chance is 20% or more; "when" is the span of
    hours at 40% or more. Snow replaces rain the same way ("snow 80%
    6 AM-noon 2.1 in") when snow is forecast.
  - The `Alert:` line appears only when the US National Weather Service
    has an active alert for the point (`api.weather.gov`, no key; skipped
    outside the US). One line per alert.
  - Plain ASCII, so the lines are easy to edit in Vim.
  - With no `[outlook]` table or no network, a single
    `- Weather: unavailable (<reason>)` line, so creating a note never fails.
- **Refresh, matched exactly.** `--update` replaces only the lines under
  `### Outlook` that start with `- Weather:`, `- Sun:` or `- Alert:`, and
  leaves anything else you wrote there alone. The "as of" time shows how
  fresh the forecast is.
- **Who refreshes (recommended).** The `daily-plan` skill runs
  `meta-notes outlook --update` on the day's note and the next day's
  note (when they exist). It runs every day in both modes, and in work
  roots after the shutdown, so the next day is always checked the evening
  before. Not the shutdown skill: personal roots have none.
- **Not now:** times of the high and low (too much for every note; in
  `--json` only), wind, UV, air quality, pollen, moon phase, frost,
  Celsius.
- **Rejected:** `local` and `location` (the human didn't like them);
  `### Almanac` (the human wasn't sure); refreshing when a note is opened
  in Vim (opening a note shouldn't need the network).

### Questions for the human

1. The note lines above (format and thresholds): OK? (Recommended.)
2. `daily-plan` refreshes today's and tomorrow's Outlook? (Recommended.)

## The human on round 3, 2026-10-08 (to the meta-notes aide)

> Yeah, let's put the "as of" in the Outlook line, I think, and then
> that'll apply to everything else underneath it. Shorten up that first
> weather line a little bit.

So: the "as of" time moves to the `### Outlook` heading (e.g.
`### Outlook (as of 9:40 PM Tue)`), covering every line under it, and
`--update` rewrites the heading's time too; the `- Weather:` line gets
shorter. Not yet an approval of the rest: question 2 (daily-plan
refreshes today's and tomorrow's Outlook) is unanswered. Still on hold.

Revised example (orchestrator):

    ### Outlook (as of 9:40 PM Tue)
    - Weather: 72/55, rain 60% 3-8 PM, 0.3 in, 4h sun
    - Sun: 7:41 AM - 7:02 PM
    - Alert: Severe Thunderstorm Warning until 6:00 PM

The `Weather:` line drops the "F" (Fahrenheit is the only unit) and the
stamp; the `Sun:` line is just the two times. `--update` matches the
heading by `### Outlook` at the start of the line and rewrites its time.

## The human on options, 2026-10-08 (to the meta-notes aide)

> Let's add in a few config and default config options. Let's make
> weather, sun, and alert default on, but have a configuration to turn
> them off. I forget whatever else you had. You had a couple interesting
> things. Go ahead and add options for moon phase and winds, but I'm
> going to turn those off to start with. Add options for first freeze or
> freeze warnings, whatever you have there. That's fine, and that'd be
> good. Those would be fun things to play around with.

So: each line is a switch in `[outlook]` in `.meta-notes`. On by default:
`weather`, `sun`, `alert`. Off by default: `moon` (phase), `wind` (speed
and gusts), `freeze` (first freeze of the season / freeze warnings; NWS
freeze and frost warnings already come through `alert`, so `freeze` is
the forecast-based "first night at or below 32" note). This replaces
"Not now" for wind, moon and frost. Still open: question 2 (daily-plan
refresh), and whether the other items the aide listed (UV, air quality,
golden hour, times of the high and low) also become off-by-default
options. Still on hold.

## The human on the other options, 2026-10-08 (to the meta-notes aide)

> I think that's enough. I really don't care about UV index, air quality,
> or golden hour unless I'm on vacation, and we can handle that
> differently anyway. If I'm traveling, you could add UV index, sure. I'm
> turned off by default. Times of the high and low: I actually really
> like that, but what I really want to see is a little chart from
> midnight to midnight or something that would show that. Either you
> could do a little sparkline chart in the sky, and that would be amazing.

So: `uv` is one more option, off by default (useful when traveling). No
air quality or golden hour. The times of the high and low become a
temperature sparkline from midnight to midnight, one character per hour,
with the low and high and their times, e.g.

    - Temps: 51 ▂▁▁▁▁▁▂▃▄▅▆▇██▇▆▅▄▃▃▂▂▂▂ 72 (low 6 AM, high 2 PM)

("in the sky" is likely speech-to-text; unclear.) The sparkline needs
Unicode block characters, so the round-3 "plain ASCII" rule gets an
exception for this line. Whether the sparkline is on or off by default
isn't said. Question 2 (daily-plan refresh) is still open. Still on hold.

## The human's answers to the last questions, 2026-10-08 (to the meta-notes aide)

> Oh yeah, I want to see the spark line. It's really cool.

> I think the daily plan should refresh the outlook, and I think you
> probably covered this, but there should be a command to refresh the
> outlook. By default, it could run today, and if there's a note for
> tomorrow, update tomorrow also. It should also take a date, so we can
> run it on a note in the future.

So: the temperature sparkline (`temps`) is on by default. `daily-plan`
refreshes the Outlook. The refresh command, with no arguments, updates
today's daily note and, when it exists, tomorrow's; `--date DAY` updates
that day's note instead (e.g. a note made days ahead). This replaces
`--update <note>` as the main form (a note path may still be accepted).
Both open questions are answered.

## Approved, 2026-10-08

The human, to the orchestrator directly, 2026-10-08 ~10:10 PM: "Weather is a go"

The orchestrator splits the build in two (worker context size):

1. mn-pqwv: `meta-notes outlook` (config, geocoding, forecast, alerts,
   the note lines and switches, `--json`) and the `### Outlook` section in
   the daily templates.
2. A follow-up task: `meta-notes outlook refresh [--date DAY]` (today and,
   when it exists, tomorrow by default) and the `daily-plan` skill step
   that runs it. Blocked by 1.
