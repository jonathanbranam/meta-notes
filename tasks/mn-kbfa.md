+++
id = "mn-kbfa"
title = "Agenda preset for the task query (vcey)"
kind = "feature"
state = "planned"
created_at = "2026-10-05T23:10:53.180Z"
updated_at = "2026-10-05T23:10:59.252101266Z"
created_by = "external:orchestrator"
watchers = ["external:orchestrator"]
size = "M"
+++

Ticket: docs/tickets/open/agenda-preset-overdue-today-and-each-day-ahead-in-one-task-q-vcey.md (approved by the human 2026-10-05).

## Goal
`meta-notes tasks --agenda`: one call that gives an agent the task picture for the coming days, so it doesn't work out dates or flags itself.

## Behaviour (decided by the orchestrator; the human approved the ticket as written)
- Sections, in order: **Overdue**, **Today**, then **one section per following day** through the horizon, each headed with its date and weekday (e.g. `2026-10-06 Tue`). Empty day sections may be omitted in text output; keep them (empty lists) in `--json`.
- **Horizon**: at least 5 days after today and through the next Monday; on Thursday or Friday, through the following Wednesday. `--through DATE` overrides it (accepts the same day syntax as `--date`). No other knobs.
- Includes started-not-due (🛫) tasks the way `--ready` does, filed under their due date (Today if they have none).
- Today's timed tasks stay under **Today** all day (date semantics, not `--at`).
- `--undated` adds an **Undated** section with open tasks that have no date. Off by default.
- Same behaviour in work and personal roots.
- `--json` works. Other `tasks` filters (`--folder`, `--tag`, etc.) combine with it if they already compose naturally; don't add new ones.

## Likely files
scripts/meta_notes/cli.py (tasks arguments), scripts/meta_notes/query.py, scripts/find_tasks.py, scripts/period.py (horizon date math if it fits there), test/unit/test_query.py / test_find_tasks.py / test_cli.py, design/specs/task-query.md, doc/meta-notes.txt (`meta-notes-cli-tasks`), README.md example line, scripts/meta_notes/prime.md (tell agents to use `--agenda` for the startup task check). Version: MINOR bump.

## Check
Unit tests for the horizon rule (Mon, Wed, Thu, Fri, Sun anchors) and for section placement (overdue, today incl. a passed timed task, a future day, 🛫 task, undated with/without `--undated`). The project's normal check (`./run_tests.sh`, `uv run pytest test/unit/`, `bridle spec check --require-ids`) green.

## Out of scope
A separate `meta-notes agenda` command; changes to skills beyond prime.md; any notes-root edits.

Model: Sonnet. Size: m.
