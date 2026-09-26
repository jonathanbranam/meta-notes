## Context

See proposal.md for motivation. `meta-notes conventions` sets the
pattern: prose in `conventions.md` beside the module, with
`<!-- generated: NAME -->` markers filled from code, and a command that
works outside a notes root. Plan note paths come from `note.py`
(`plan/daily/YY-QN/YYYY-MM-DD Ddd.md`, `plan/week/YY-QN/<monday>.md`,
`plan/quarter/YYYY-QN.md`, `plan/year/YYYY.md`); tag groups from
`TAG_GROUPS` in `time_tracking.py`; skill names from
`init.shipped_skills()`; archive paths from `ops.archive_item`
(`archive/<original path>`).

The user's `docs/work-notes-claude.md` is the raw material. Its system
parts are wrong in places (see proposal); its personal parts (8:00–17:00,
lunch at 11:30, breaks, shutdown block, expenses and CBTs, tabs, Slack)
aren't the plugin's.

## Goals / Non-Goals

**Goals:**
- One command gives an agent everything it needs to work in any notes
  root: structure, conventions, and where to look for the rest.
- Nothing in the guide can drift from the code it describes.

**Non-Goals:**
- A Claude Code hook. Hooks aren't allowed in the work Claude sandbox,
  so priming must work from `CLAUDE.md` alone; `init` does not touch
  `.claude/settings.json`.
- Writing or editing `CLAUDE.md`, and config for personal preferences
  (a `[planning]` table in `.meta-notes`). The default working day goes
  in the guide's prose instead; see decision 6.
- Live state in the guide (active projects, due tasks). Those are one
  command away and would make the guide long and slow.
- Changing the skills. They keep running `meta-notes conventions`; a
  primed session reads the conventions twice, about 5.6 KB.

## Decisions

### 1. A command, not a generated file

`meta-notes prime` prints the guide each time. A file written by `init`
and `@`-imported from `CLAUDE.md` would go stale on every plugin update
until `init` is re-run, and couldn't show today's plan paths. Bash
output in Claude Code is read in full up to about 30,000 characters, so
a 20,000-character budget is safe. This is the `bd prime` approach
without its hook, which the work sandbox doesn't allow.

### 2. Prose in `prime.md`, generated blocks from code

`prime.py` mirrors `conventions.py`: `prime.md` holds the prose with
markers `today-paths`, `daily-sections`, `weekly-sections`, `tag-groups`,
`skills`, and `conventions`. The `conventions` marker expands to
`conventions.run()` with its top-level `# meta-notes conventions`
heading demoted to `##`, and every heading below it demoted one level,
so the guide is one document. Unknown markers raise, as in
`conventions.render`.

Today's paths reuse `note.py`'s path function for each kind rather than
repeating the patterns. Template sections are the `##`/`###` headings of
the root's template, or the shipped template, with front matter and
`{{% %}}` blocks ignored; a missing or unreadable root template falls
back to the shipped one.

### 3. Root optional

`cmd_prime` resolves the root like other commands but treats "no root"
as data (`root: null` and a leading line), not an error, like
`conventions`. An agent started in the wrong directory then learns why
the paths don't exist instead of getting nothing.

### 4. What the guide says about the user's doc

From `docs/work-notes-claude.md`, corrected against the code:

| Doc says | Guide says |
|---|---|
| PARA, daily notes in `resource/daily-notes` | PPARA, `plan/daily/YY-QN/` |
| Weekly plan `resource/plan/week/Plan <date>.md` | `plan/week/YY-QN/<monday>.md` |
| Template `Daily Note Template.md` | `resource/template/daily.md` |
| `Project List.md`, `Project History.md` | `meta-notes projects`; archive |
| Every checkbox is a task | Only with 📅 or 🛫 (conventions) |
| Any other status is partial | Generated status table |
| Work ends at 17:00; plan no work after | Same, and the 17:00–18:00 rows are for personal events |
| Project `Planning.md` | Not described; project notes are free-form beyond `Home.md`, `Tasks.md`, `Meetings & Notes.md` |

Kept from the doc: folder and note naming (Title Case notes), `Home.md`
kept short, `Tasks.md` with an optional `Completed` section, dated
headings newest first, areas holding or linking projects, general
meeting notes under `resource/`, other file types allowed.

The personal parts go back into `docs/work-notes-claude.md`, rewritten
as a `CLAUDE.md` for the work root that starts with the `prime` line.

### 5. Init check is an item, not a warning

The `claude-md` item fits init's existing report (`kind`, `path`,
`status`), so JSON and `:MetaNotesInit` pick it up through the message
table without a new field. It's not a warning because init's "CLI on
PATH" scenario requires no warnings in an empty directory, and a
missing line is a suggestion, not a problem.

### 6. Working hours are a stated default

The guide gives the working day as 08:00–17:00, Monday to Friday, and
says not to plan work after 17:00. The daily template's time block runs
to 18:00 on purpose: the extra hour holds after-work personal events as
reminders, and occasional late work is logged there. The guide says
this so an agent doesn't trim the table or fill 17:00–18:00 with work.
`calendar` changes its 9:00 start to 8:00 to agree with `weekly-plan`.
A root's `CLAUDE.md` can override the hours; a config setting waits
until a root actually needs different ones.

## Risks / Trade-offs

- [The agent skips the `CLAUDE.md` instruction] → The line is short and
  imperative; `CLAUDE.md` is reloaded after compaction. Hooks aren't an
  option at work, so if this proves unreliable, the skills can run
  `prime` instead of `conventions` as their first step.
- [Guide grows past the budget] → A test asserts the size in a root with
  every shipped skill; the budget is in the spec.
- [Hand-written prose drifts from specs for projects and archive] →
  Prose states rules the specs already fix (fields, archive path), and
  tests assert the key phrases (`meta-notes archive`,
  `archive/`, `Home.md`).

## Migration Plan

After the change ships: add the `prime` line to each root's `CLAUDE.md`
(init prints it), and replace the work root's `CLAUDE.md` with the
trimmed `docs/work-notes-claude.md`. Nothing to roll back; removing the
line stops priming.
