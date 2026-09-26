## Why

An agent started in a notes root knows only what the root's `CLAUDE.md`
tells it. Outside the ceremony skills, which run `meta-notes conventions`,
nothing explains the PPARA layout, where plan notes live, what a project's
home note and fields are, how archiving works, or which commands find
things. The hand-written `docs/work-notes-claude.md` (the work laptop's
`CLAUDE.md`) fills the gap but has drifted from the plugin: it puts daily
notes in `resource/daily-notes/` and weekly plans in `resource/plan/week/`,
treats every checkbox as a task, lists partial statuses wrongly, and
predates project fields, `#next`/`#review`/`#deadline`, and the CLI. A
hand-copied file per root will keep drifting.

Beads solves the same problem with `bd prime`: a command that prints a
short operating manual for the agent, so the manual ships with the tool
and always matches it. meta-notes already does this for syntax
(`meta-notes conventions`, generated from the code); this change does it
for the whole notes root.

## What Changes

- **`meta-notes prime`** prints a guide to the notes root as markdown for
  an agent to read at the start of a session:
  - the PPARA folders and what goes in each; folder names lowercase with
    dashes, note names Title Case with spaces
  - the plan notes: today's daily, weekly, quarterly, and yearly paths,
    and how to create one
  - projects: a single note or a folder with `Home.md`, the common
    project files (`Tasks.md`, `Meetings & Notes.md` with dated headings,
    newest first), fields and status, `#next`, `#review`, `#deadline`,
    `meta-notes projects` as the project list, and converting a project
    to an area
  - areas, resources (including general meeting notes), and the archive:
    `archive/<original path>`, `status: archived` and `archived:` on a
    project, links that keep resolving, and `meta-notes archive` as the
    only way to archive
  - the working day: 08:00–17:00, Monday to Friday, nothing work-related
    planned after 17:00, and the time block running to 18:00 for
    after-work personal events
  - the daily note's time log and time block, with the time report's
    tag groups
  - the commands for finding things, and the shipped skills
  - that personal preferences (routines, weekly admin, other hours) are
    in the root's `CLAUDE.md` and override the guide
  - the full conventions, as `meta-notes conventions` prints them

  Code-defined parts are generated, as in `conventions`. `--json` gives
  `version`, `root`, and `text`.
- **One line in `CLAUDE.md`.** Users add ``Run `meta-notes prime` at the
  start of every session and follow it.`` to the root's `CLAUDE.md`.
  `CLAUDE.md` is reloaded after `/clear` and compaction, so the agent
  sees the instruction again. `meta-notes init` checks for the line and,
  when it's missing, says what to add. It never edits `CLAUDE.md`.
- `docs/work-notes-claude.md` is reduced to the personal preferences
  (working hours, lunch, breaks, the shutdown block, the weekly admin
  checklist), the starting point for the work root's `CLAUDE.md`.
  `project/Project List.md` and `Project History.md` are dropped:
  `meta-notes projects` is the list and the archive is the history.
- The `calendar` skill's workday changes from 9:00–17:00 to 8:00–17:00,
  matching `weekly-plan` and the guide.

## Capabilities

### New Capabilities
- `agent-prime`: `meta-notes prime`: content, generated parts, JSON,
  size, behavior outside a notes root

### Modified Capabilities
- `conventions`: shorter: only 📅 is named as the due emoji, and the
  status characters, tag aliases, and ceremony markers are sentences,
  not tables
- `init`: checks the root's `CLAUDE.md` for the `meta-notes prime` line
  and reports it

## Impact

- `scripts/meta_notes/prime.py`, `scripts/meta_notes/prime.md`: new,
  following `conventions.py`/`conventions.md`
- `scripts/meta_notes/cli.py`: `prime` subcommand, init report line
- `scripts/meta_notes/init.py`: the `CLAUDE.md` check
- `autoload/meta_notes/notes.vim`: `:MetaNotesInit` shows the check
- `test/unit/test_prime.py` (new), `test/unit/test_init.py`,
  `test/unit/test_cli.py`
- `doc/meta-notes.txt`, `README.md`: the command and the `CLAUDE.md` line
- `skills/calendar/SKILL.md`: workday hours
- `scripts/meta_notes/conventions.md`, `conventions.py`: shorter text
- `docs/work-notes-claude.md`: trimmed to personal preferences
- `scripts/meta_notes/__init__.py`: MINOR version bump on archive
