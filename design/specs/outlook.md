# outlook Specification

## Purpose
Specifies `meta-notes outlook`, which prints a day's weather, temperatures, sun times and weather alerts for a place, and the `### Outlook` section of the daily note templates that it fills.

## Requirements

### Requirement: Outlook command  {#r-0a1c}
The CLI SHALL provide `meta-notes outlook [--date DAY] [--location PLACE] [--json]`, which prints the heading `### Outlook (as of <time> <Day>)` and one `- Name: ...` line for each line that is on. `--date` SHALL default to today. `--location` SHALL be a city and state as in `Mason, OH`, or a ZIP code, and SHALL override the configured location. `meta-notes outlook weather` and `meta-notes outlook sun` SHALL print only their own line, without a heading, and SHALL fail with an error when the outlook can't be made.

#### Scenario: Default output  {#s-0a2d}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes outlook` with a configured location
- **THEN** the output SHALL be the heading followed by the Weather, Temps and Sun lines, and an Alert line for each active alert

#### Scenario: One line  {#s-0a3e}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes outlook sun`
- **THEN** the output SHALL be the single line `- Sun: <rise> - <set>`

### Requirement: Outlook settings  {#r-0a4f}
The command SHALL read the `[outlook]` table in `.meta-notes`: `location` (a city and state, or a ZIP code), and a boolean switch for each line. `weather`, `temps`, `sun` and `alert` SHALL default to on; `moon`, `wind`, `freeze` and `uv` SHALL default to off. A switch that is not a boolean SHALL be an error.

#### Scenario: Switch off  {#s-0a50}
*Verification*: **non-executable**
- **WHEN** `[outlook]` has `sun = false`
- **THEN** the output SHALL have no Sun line

### Requirement: Outlook lines  {#r-0a61}
The lines SHALL be, in this order and only when on:
- `Weather: <high>/<low>[, rain|snow <chance>% [<hours>][, <amount> in]], <n>h sun`, in Fahrenheit and inches. Rain or snow SHALL show only when the chance is 20% or more, or snow is forecast; snow replaces rain. The hours SHALL span the hours with a chance of 40% or more.
- `Temps: <low> <sparkline> <high> (low <hour>, high <hour>)`, one block character per hour from midnight to midnight. This is the only line that is not ASCII.
- `Sun: <sunrise> - <sunset>`.
- `Alert: <event> until <time>`, one per active National Weather Service alert that overlaps the day. Alerts SHALL be fetched only for a US location.
- `Moon: <phase> (<n>% lit)`; `Wind: <n> mph, gusts <n>`; `Freeze: low <n>`, only when the low is 32 or less; `UV: <n>`.

#### Scenario: Rain  {#s-0a72}
*Verification*: **non-executable**
- **WHEN** the chance of rain is 60% from 3 PM to 8 PM with 0.3 in and 4 hours of sun
- **THEN** the Weather line SHALL read `Weather: 72/51, rain 60% 3-8 PM, 0.3 in, 4h sun` for a high of 72 and low of 51

### Requirement: Outlook data sources  {#r-0a83}
The command SHALL use Open-Meteo for geocoding and the forecast and the National Weather Service API for alerts, with no key and the Python standard library only. Coordinates found for a place SHALL be cached in `.meta-notes-cache/`. A city with no state that matches several places SHALL be an error that lists them.

#### Scenario: Cached place  {#s-0a94}
*Verification*: **non-executable**
- **WHEN** the same place is looked up twice
- **THEN** the second run SHALL make no geocoding request

### Requirement: Outlook in note templates  {#r-0aa5}
`templates/daily.md` and `templates/daily-personal.md` SHALL fill a `### Outlook` section near the top through a `{{% python ... outlook --date <note date> %}}` block. When there is no location or no network, `meta-notes outlook` without a subcommand SHALL print the heading and one `- Weather: unavailable (<reason>)` line and exit 0, so creating a note never fails.

#### Scenario: Offline  {#s-0ab6}
*Verification*: **non-executable**
- **WHEN** a daily note is created with no network
- **THEN** the note SHALL be created with `- Weather: unavailable (<reason>)` under the Outlook heading

### Requirement: Outlook refresh  {#r-0ac7}
The CLI SHALL provide `meta-notes outlook refresh [--date DAY] [--location PLACE] [--json]`. With no `--date` it SHALL refresh today's daily note and, when it exists, tomorrow's; with `--date` it SHALL refresh only that day's note. Refresh SHALL rewrite the time in the `### Outlook (as of ...)` heading and replace the lines under it that the command writes, keep any other line there, and write through the guarded note write. A note that is missing, has no `### Outlook` heading, or whose outlook can't be made SHALL be left unchanged, with a status line saying why.

#### Scenario: Today and tomorrow  {#s-0ad8}
*Verification*: **non-executable**
- **WHEN** the user runs `meta-notes outlook refresh` and tomorrow's daily note exists
- **THEN** both notes SHALL have a new heading time and new Outlook lines, and a line the user wrote under the heading SHALL remain

#### Scenario: No heading  {#s-0ae9}
*Verification*: **non-executable**
- **WHEN** the note has no `### Outlook` heading
- **THEN** the note SHALL be unchanged and the status SHALL be `no heading`
