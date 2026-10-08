+++
id = "mn-pqwv"
title = "Weather command: tomorrow's forecast from a free no-key API"
kind = "feature"
state = "open"
created_at = "2026-10-08T03:22:20.510Z"
updated_at = "2026-10-08T03:22:41.429382029Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

original id: pqwv

`meta-notes outlook`: the day's weather, sun and alerts for the daily note. The ticket (docs/tickets/open/weather-command-tomorrow-s-forecast-from-a-free-no-key-api-pqwv.md) is the spec. Read it all: later sections replace earlier ones. Settled shape: rounds 2 and 3, "Revised example", and the human's answers on options, other options and the last questions.

Approved: the human, 2026-10-08: "Weather is a go" (on the ticket).

This task (part 1 of 2):
- `meta-notes outlook [--date DAY] [--location PLACE] [--json]` prints the `### Outlook (as of <time> <Day>)` heading and its lines; `outlook weather`, `outlook sun` print one line. `--date` defaults to today.
- Lines and switches in `[outlook]` in `.meta-notes`: `location` ("Mason, OH" or "45040"); on by default `weather`, `temps` (the midnight-to-midnight sparkline line), `sun`, `alert`; off by default `moon`, `wind`, `freeze`, `uv`. Formats as in the ticket's examples; the sparkline line is the only non-ASCII one.
- Open-Meteo geocoding (cache coordinates in .meta-notes-cache/) and forecast; NWS api.weather.gov alerts (US only, User-Agent, skipped elsewhere). Standard library only (urllib); network calls behind one small function so tests use canned JSON, no live calls in tests.
- No config or no network: a single `- Weather: unavailable (<reason>)` line, exit 0 when run from a template, so note creation never fails.
- `templates/daily.md` and `templates/daily-personal.md` get the `### Outlook` section near the top, filled by a `{{% ... %}}` block like the existing find_tasks ones, for the note's date. Update test/fixtures/templates if the template tests need it.
- Docs: README (Command Line list and examples, a short Outlook config section), doc/meta-notes.txt (a meta-notes-cli-outlook section, meta-notes-config). Minor version bump.

Model: Sonnet. Size: L (keep your context well under 200K; read only the files you need).
Files likely touched: new scripts/meta_notes/outlook.py, scripts/meta_notes/cli.py, scripts/meta_notes/config.py, templates/daily*.md, test/unit/test_outlook.py, test/unit/test_cli.py (if it lists commands), README.md, doc/meta-notes.txt, scripts/meta_notes/__init__.py (version).
Verify: ./run_tests.sh green once. One manual live run of `meta-notes outlook --location 45040` is fine; report its output in your done note.
Out of scope, in the follow-up task: the refresh command and the daily-plan skill step. Not now: Celsius, air quality, golden hour.
