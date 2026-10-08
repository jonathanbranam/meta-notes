+++
id = "mn-j7e3"
title = "Outlook refresh command and the daily-plan step (pqwv part 2)"
kind = "feature"
state = "planned"
created_at = "2026-10-08T03:22:41.668Z"
updated_at = "2026-10-08T03:45:09.884338671Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
+++

Part 2 of 2 of ticket pqwv (docs/tickets/open/weather-command-tomorrow-s-forecast-from-a-free-no-key-api-pqwv.md); part 1 is mn-pqwv (`meta-notes outlook`), which must merge first.

Approved: the human, 2026-10-08: "Weather is a go" (on the ticket). Their words on refresh: "there should be a command to refresh the outlook. By default, it could run today, and if there's a note for tomorrow, update tomorrow also. It should also take a date, so we can run it on a note in the future." And: "the daily plan should refresh the outlook".

- `meta-notes outlook refresh [--date DAY] [--json]`: with no date, refreshes today's daily note and, when it exists, tomorrow's; with `--date`, that day's note only. A note path argument may also be accepted. Refresh rewrites the `### Outlook (as of ...)` heading's time and replaces only the lines under it that the command writes (`- Weather:`, `- Temps:`, `- Sun:`, `- Alert:` and the optional lines), leaving anything else there alone. Race-safe through the existing note_write path. A note without the heading: unchanged, with a message.
- The daily-plan skill (skills/daily-plan) runs `meta-notes outlook refresh` as a step, both modes.
- Docs: README, doc/meta-notes.txt, the skills table if it changes. Patch or minor bump per .bridle/rules/versioning.md.

Model: Sonnet. Size: M.
Files likely touched: scripts/meta_notes/outlook.py, scripts/meta_notes/cli.py, skills/daily-plan/SKILL.md, test/unit/test_outlook.py, README.md, doc/meta-notes.txt, version.
Verify: ./run_tests.sh green once; tests for: today plus tomorrow, tomorrow missing, --date, user lines under the heading kept, no heading.
Out of scope: refreshing on note open (rejected on the ticket).
