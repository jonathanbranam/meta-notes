# Tasks

## 1. CLI filters

- [ ] 1.1 In `calendar.py`, add word-start person matching over the organizer and every attendee who is a person (design decision 2) and `--search` substring matching over title, location, and description; apply them per occurrence in `agenda()` and add `matches` to matching events; verify with `test_calendar.py` tests for "First name as a prefix", "Name found in the email address", "Attendee past the list cap", "Two names", "Word start only", an organizer-only match, "Topic in the description", and "Filters combined"
- [ ] 1.2 Drop days without matches when a filter is given, print `No matching events.` when none match, and leave unfiltered output unchanged (no `matches`); verify with tests for "Only matching days", "No matches" (text and `--json`), "Matches in JSON" (the exact `matches` object), and an unfiltered run with no `matches` key
- [ ] 1.3 Add repeatable `--with NAME` and `--search TEXT` to the `calendar` subcommand in `cli.py`, with a NAME lacking letters or digits as an error; verify with `test_cli.py`-style tests through `cli.main` in `test_calendar.py` for both options and the error
- [ ] 1.4 Document `--with`, `--search`, `matches`, and filtered output under `*meta-notes-cli-calendar*` in `doc/meta-notes.txt` and add a filtered example to README's Command Line examples; verify `:helptags doc` reports no errors

## 2. Skill

- [ ] 2.1 Write `skills/calendar/SKILL.md` per design decision 4: frontmatter description per the `calendar-skill` "ships with the plugin" requirement; PATH check; period rules with the 28-day default; the command lines for people (`--with`), topics (`--search`), and plain agendas; retry and ambiguity rules; the 1-1 rule; the answer format with export age and warnings; failure fallbacks; read-only; verify by reading it against every `calendar-skill` scenario
- [ ] 2.2 Check `init` links it: extend `test_init_shipped_skills_includes_project_review` (or add a test) to assert `calendar` is in `init.shipped_skills()`; verify `pipenv run pytest test/unit/test_init.py`
- [ ] 2.3 Add `calendar` to README's Planning Skills table and to the skills list in `doc/meta-notes.txt` (`*meta-notes-skills*`); verify both mention it

## 3. Integration

- [ ] 3.1 In a notes root with a real export, ask Claude "do I have a 1-1 with <name> next week", "find any meetings with <name>", and "find all meetings about <topic>", and confirm each runs `meta-notes calendar --json` with the right `--date`, `--with`, or `--search` and matches Google Calendar; then run `pipenv run pytest test/unit/` and `./run_tests.sh`
