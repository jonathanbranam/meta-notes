## Context

The CLI (`scripts/meta_notes/cli.py`) dispatches subcommands to modules in
`scripts/meta_notes/`. `note` and `task` are subcommand groups; a parser
with `resolves_root` false (as `init` and `--version` use) runs without a
notes root. Every command returns an `Output`, so `--json` and error
handling come for free.

The pieces this change builds on:

- `scripts/tasks.py`: `CHECKBOX_PATTERN`, `is_task`, `DUE_EMOJIS`, and
  `_char_to_status` (the status mapping, private today).
- `scripts/tags.py`: `TAG_PATTERN`, `TAG_ALIASES`, `canonical_tag`, shared
  by task queries, time logs, and `task update`.
- `scripts/find_tasks.py`: `collect_tasks` parses every task under a root;
  `scripts/meta_notes/query.py` turns tasks into JSON dicts.
- `scripts/period.py`: `parse_period` for the shared `--date` syntax.
- `scripts/meta_notes/note.py`: `periodic_note(kind, day)` gives the daily
  and weekly note paths; weeks start on Monday (`template.week_start`).
- `task-update` is archived (0.4.0). `project-brief` (home note and field
  parsing) is not yet implemented. `task-age` is deferred: nothing here
  reads git history, `git blame`, or file mtimes.

See proposal.md for motivation and the specs for behavior.

## Goals / Non-Goals

**Goals:**
- Each new command is a thin read-only module over parsers that already
  exist, so a skill, the dashboard, and Vim see the same answers.
- Skills hold ceremony steps and judgment only; syntax lives in
  `meta-notes conventions`, and every read or edit is a CLI call.

**Non-Goals:**
- Reminders, the dashboard, and calendar access (screenshots only).
- Holiday calendars: a workday is Monday to Friday.
- Git writes from the CLI. The shutdown commit is made by the skill with
  `git`, after the user confirms it.
- Migrating existing daily and weekly notes to the new sections.

## Decisions

### One module per command

`ceremony.py`, `projects.py`, and `conventions.py` in
`scripts/meta_notes/`, each with a `run(...)` that returns text lines and a
JSON dict, and a `today` parameter so tests fix the date. `cli.py` adds
`ceremony status` as a subcommand group (like `task update`, leaving room
for `ceremony mark` later), and `projects` and `conventions` as plain
subcommands. `conventions` sets `resolves_root` false.

*Alternative:* one `planning.py` for all four. They share almost nothing,
and one module per command matches `ops.py`, `note.py`, and `time.py`.

### Ceremony markers reuse the checkbox pattern

`ceremony.py` scans the note's lines with `tasks.CHECKBOX_PATTERN`, strips
the checkbox and a trailing `✅ YYYY-MM-DD`, and compares the rest,
lowercased and trimmed, with the marker name. Status comes from
`tasks._char_to_status`, which this change makes public as
`char_to_status`, so "done" means exactly what it means in queries. Note
paths come from `note.periodic_note`, so `ceremony status` looks where
`meta-notes note daily|weekly` writes. `--date` is checked with the strict
`YYYY-MM-DD` validator `task update` uses (regex, then
`date.fromisoformat`), which rejects ranges and months as usage errors.

*Alternative:* `parse_period` and reject START != END. That would still
accept a range like `2026-09-25..2026-09-25`, which the spec rejects, and
its errors talk about periods rather than a single day.

### Projects: one task pass, then buckets

`projects.py` lists `project/*.md` and `project/*/`, reads each home note's
fields, then parses every task in the root once with
`find_tasks.collect_tasks` and assigns each task to projects by path prefix
and by canonical tag. Last review and `no-next` come from that pass.

The latest date comes from a date scan: a `\d{4}-\d{2}-\d{2}` search over
each project file's path and contents, plus the text of the project's
tagged tasks, keeping matches that `date.fromisoformat` accepts and that
are on or before today. Abandoned projects are months or years stale, so
dates written in the notes (meeting notes, task dates, ✅ dates, daily-note
links) separate them from active ones without git history.

*Alternative:* git history or file mtimes. History needs blame and log
per file and is deferred with `task-age`; mtimes change on moves and link
rewrites, which touch files nobody worked on.

Field parsing (home note, first list after the title, `key: value`) lives
in `scripts/meta_notes/project.py`, shared with `project-brief` and
`archive-project-status`. `archive-project-status` created it with
`project_for`, `home_note`, `read_fields`, and `set_fields`; this change
reuses it (see `openspec/specs/project-fields`).

*Alternative:* call `project brief` per project. That repeats the full
task parse once per project.

### Conventions: a markdown file with generated blocks

`scripts/meta_notes/conventions.md` holds the prose. Code-defined parts are
marked with HTML comments (`<!-- generated: statuses -->`,
`<!-- generated: due-emoji -->`, `<!-- generated: tag-aliases -->`), which
`conventions.py` replaces with tables built from `tasks.py` and `tags.py`.
An unreplaced marker is invisible when rendered. A unit test checks that
every marker is replaced and that each alias in `TAG_ALIASES` appears in
the output.

*Alternative:* render with the note template engine. Its `{{ }}` syntax
and command blocks are for notes; plain markers keep the file readable.

### Skills share a fixed shape

Each `SKILL.md` has frontmatter (`name`, a `description` saying when to
use it and, for `project-review`, that task cleanup is not it) and then,
in order: time budget, "run `meta-notes conventions` first", hard rules,
numbered steps with the CLI call for each, and a stop section. Steps name
exact commands (for example `meta-notes tasks --tag wait --json`) so the
agent doesn't improvise queries. The six skills are written after the CLI
commands exist, against the real output.

*Alternative:* draft skills first against today's tools. Every dependency
except `project-brief` is now in, so writing them once against the final
commands avoids a rewrite.

### Template sections

`templates/daily.md`: the two markers go in a short checklist under the
Week Plan link, and `## Follow Up` goes after `## Notes`.
`templates/weekly.md`: the two markers go under the Quarterly Plan link,
and `## Review` and `## Plan` go before `## Notes`. The rendered fixtures in
`test/fixtures/templates/` are regenerated to match.

### `#waiting` alias

Added to `tags.TAG_ALIASES`. Time logs share the table, so `#waiting` time
entries now total under `#wait`, which is the intent.

## Risks / Trade-offs

- [Skill behavior can't be unit tested] → Each skill is checked by a
  scripted run in a scratch notes root (fixture notes, a fixed date) and by
  reading it end to end against its spec requirement.
- [A stale project mentions a recent date (a link to this week's daily
  note, a pasted date)] → It reads as active; the monthly project review
  still reaches it through `review-overdue`.
- [An active project with no dates in it] → It is flagged
  `no-recent-activity`; the warning never blocks, and adding a dated task
  or note clears it.
- [Existing notes have no markers or sections] → Missing counts as not
  done; skills add a missing section when they write to it.
- [Marker text typed differently (`Shutdown complete.`)] → Case and
  surrounding whitespace are ignored; other variations count as missing,
  which `ceremony status` reports as `(no marker)`.

## Migration Plan

1. Wait for `project-brief` (and ideally `archive-project-status`) to be
   archived; `projects` reuses the shared field parser.
2. Land the CLI pieces (alias, conventions, ceremony status, projects)
   with tests, then the templates, then the skills.
3. After updating, the user re-runs `meta-notes init` so the five new
   skills are linked into the notes root. Existing templates are left
   alone; `init --force` or a manual edit brings in the new sections.
4. MINOR version bump on archive. Rollback is reverting the change; no
   note content is migrated.
